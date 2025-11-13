<script lang="ts">
import type { CitationLinkTarget } from '../types';

interface RawGroupEntry {
	index: number;
	pages?: string[];
}

interface GroupView {
	citationIndex: number;
	defaultTarget: string | null;
	pageLinks: { label: string; url: string | null }[];
}

export let id;
export let token;
export let onClick: Function = () => {};
export let sourceTargets: CitationLinkTarget[] = [];

	const stripDocPrefix = (hint: string): string => {
		const trimmed = hint.trim();
		const lastColon = trimmed.lastIndexOf(':');
		if (lastColon !== -1) {
			return trimmed.slice(lastColon + 1).trim();
		}
		return trimmed;
	};

	const deriveAnchorFromHint = (hint: string | null | undefined): number | null => {
		if (!hint) return null;
		const normalized = stripDocPrefix(hint);
		const match = normalized.match(/\d+/);
		if (!match) return null;
		const anchor = Number(match[0]);
		return Number.isNaN(anchor) ? null : anchor;
	};

	const canApplyAnchor = (url: string | null | undefined) => {
		if (typeof url !== 'string') return false;
		return /\/files\//.test(url);
	};

	const buildUrlWithAnchor = (url: string | null | undefined, anchor: number | null) => {
		if (!url || anchor === null || !canApplyAnchor(url)) return null;
		return `${url.replace(/#page=\d+/i, '')}#page=${anchor}`;
	};

	const fallbackAnchorUrl = (hint: string | null | undefined, entry: CitationLinkTarget | undefined) => {
		if (!entry?.defaultTarget) return null;
		const anchor = deriveAnchorFromHint(hint);
		if (anchor === null) return null;
		return buildUrlWithAnchor(entry.defaultTarget, anchor);
	};

	const formatDisplayHint = (hint: string | null | undefined): string => {
		if (!hint) return '';
		const normalized = stripDocPrefix(hint);
		const prefixMatch = normalized.match(/^[^\d]+/);
		const numericMatch = normalized.match(/\d+/);
		if (!numericMatch) return normalized;
		const prefix = prefixMatch ? prefixMatch[0] : '';
		return `${prefix}${numericMatch[0]}`;
	};

	const extractAttributes = (input: string): Record<string, string> => {
		const regex = /([\w-]+)="([^"]*)"/g;
		const attrs: Record<string, string> = {};
		let match;

		while ((match = regex.exec(input)) !== null) {
			attrs[match[1]] = match[2];
		}

		return attrs;
	};

	const decodeGroups = (payload?: string): RawGroupEntry[] => {
		if (!payload) return [];

		try {
			const parsed = JSON.parse(decodeURIComponent(payload));
			if (!Array.isArray(parsed)) return [];
			return parsed.filter(
				(entry): entry is RawGroupEntry =>
					entry && typeof entry === 'object' && typeof entry.index === 'number'
			);
		} catch (error) {
			return [];
		}
	};

	const derivePageHints = (raw: string | null | undefined): string[] => {
		if (!raw) return [];

		const trimmed = raw.trim();
		if (!trimmed) return [];

		const normalized = stripDocPrefix(trimmed);
		const variants = new Set<string>();
		variants.add(trimmed);
		if (normalized !== trimmed) {
			variants.add(normalized);
		}

		if (normalized.startsWith('(') && normalized.endsWith(')') && normalized.length > 2) {
			variants.add(normalized.slice(1, -1));
		}

		const alphaNumeric = normalized.replace(/^[^0-9]+/, '');
		if (alphaNumeric && alphaNumeric !== normalized) {
			variants.add(alphaNumeric);
		}

		const numericMatches = normalized.match(/\d+/g);
		numericMatches?.forEach((match) => {
			variants.add(match);
			variants.add(String(Number(match)));
		});

		return Array.from(variants).filter((value) => value.length > 0);
	};

	const resolvePageTarget = (label: string, entry: CitationLinkTarget | undefined) => {
		if (!entry) return null;

		const candidates = derivePageHints(label);
		for (const candidate of candidates) {
			const target = entry.pageTargets?.[candidate];
			if (target) return target;
		}

		if (entry.defaultTarget && canApplyAnchor(entry.defaultTarget)) {
			return entry.defaultTarget;
		}

		return fallbackAnchorUrl(label, entry) ?? entry.defaultTarget ?? null;
	};

	const buildGroupView = (groups: RawGroupEntry[]): GroupView[] => {
		return groups
			.map((group) => {
				const citationIndex = Number(group.index);
				if (!Number.isInteger(citationIndex) || citationIndex <= 0) {
					return null;
				}

				const entry = sourceTargets?.[citationIndex - 1];
				if (!entry) return null;

				const pageLinks = (group.pages ?? []).map((rawLabel) => ({
					label: formatDisplayHint(rawLabel) || rawLabel,
					url: resolvePageTarget(rawLabel, entry) ?? entry.defaultTarget ?? null
				}));

				return {
					citationIndex,
					defaultTarget: entry.defaultTarget ?? null,
					pageLinks
				};
			})
			.filter((value): value is GroupView => value !== null);
	};

	let attributes: Record<string, string> = {};
	let groups: GroupView[] = [];
	let primaryGroup: GroupView | null = null;

	$: attributes = token?.text ? extractAttributes(token.text) : {};
	$: groups = buildGroupView(decodeGroups(attributes.data));
	$: primaryGroup = groups.length > 0 ? groups[0] : null;

	const handleClick = (citationIndex: number) => {
		onClick(id, String(citationIndex), undefined);
	};
</script>

{#if groups.length > 0}
	<span class="inline-flex flex-wrap items-center gap-1 text-xs font-medium translate-y-[2px] px-2 py-0.5 dark:bg-white/5 dark:text-white/60 dark:hover:text-white bg-gray-50 text-black/60 hover:text-black transition rounded-lg">
		{#if primaryGroup?.defaultTarget}
			<a
				class="whitespace-nowrap underline-offset-2 hover:underline"
				href={primaryGroup.defaultTarget}
				target="_blank"
				rel="noopener noreferrer"
			>
				†
			</a>
		{:else}
			<button
				class="whitespace-nowrap underline-offset-2 hover:underline"
				on:click={() => handleClick(primaryGroup?.citationIndex ?? groups[0].citationIndex)}
			>
				†
			</button>
		{/if}
		<span>(</span>
		{#each groups as group, groupIndex}
			<span class="inline-flex flex-wrap items-center gap-1">
				{#if group.defaultTarget}
					<a
						class="whitespace-nowrap underline-offset-2 hover:underline"
						href={group.defaultTarget}
						target="_blank"
						rel="noopener noreferrer"
					>
						{group.citationIndex}
					</a>
				{:else}
					<button
						class="whitespace-nowrap underline-offset-2 hover:underline"
						on:click={() => handleClick(group.citationIndex)}
					>
						{group.citationIndex}
					</button>
				{/if}
				{#if group.pageLinks.length > 0}
					<span>:</span>
					{#each group.pageLinks as page, pageIndex}
						{#if page.url}
							<a
								class="whitespace-nowrap underline-offset-2 hover:underline"
								href={page.url}
								target="_blank"
								rel="noopener noreferrer"
							>
								{page.label}
							</a>
						{:else}
							<button
								class="whitespace-nowrap underline-offset-2 hover:underline"
								on:click={() => handleClick(group.citationIndex)}
							>
								{page.label}
							</button>
						{/if}
						{#if pageIndex < group.pageLinks.length - 1}
							<span>,</span>
						{/if}
					{/each}
				{/if}
			</span>
			{#if groupIndex < groups.length - 1}
				<span>,</span>
			{/if}
		{/each}
		<span>)</span>
	</span>
{/if}
