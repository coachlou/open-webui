<script lang="ts">
import type { CitationLinkTarget } from '../types';

export let id;
export let token;
export let onClick: Function = () => {};
export let sourceTargets: CitationLinkTarget[] = [];

let attributes: Record<string, string | undefined> = {};
let decodedTitle: string | undefined;
let targetUrl: string | null = null;
let pageHint: string | null = null;
let citationIndex: number | null = null;
let displayLabel: string = '';
let displayHints: string[] = [];
let pageLinks: { label: string; url: string | null }[] = [];

	function extractAttributes(input: string): Record<string, string> {
		const regex = /([\w-]+)="([^"]*)"/g;
		let match;
		let attrs: Record<string, string> = {};

		// Loop through all matches and populate the attributes object
		while ((match = regex.exec(input)) !== null) {
			attrs[match[1]] = match[2];
		}

		return attrs;
	}

	// Helper function to return only the domain from a URL
	function getDomain(url: string): string {
		const domain = url.replace('http://', '').replace('https://', '').split(/[/?#]/)[0];

		if (domain.startsWith('www.')) {
			return domain.slice(4);
		}
		return domain;
	}

	// Helper function to check if text is a URL and return the domain
	function formattedTitle(title: string): string {
		if (title.startsWith('http')) {
			return getDomain(title);
		}

		return title;
	}

	const getDisplayTitle = (title: string) => {
		if (!title) return 'N/A';
		if (title.length > 30) {
			return title.slice(0, 15) + '...' + title.slice(-10);
		}
		return title;
	};

	$: attributes = extractAttributes(token.text);
	$: decodedTitle = (() => {
		if (!attributes.title) return undefined;
		try {
			return decodeURIComponent(attributes.title);
		} catch (e) {
			return attributes.title;
		}
	})();
	const derivePageHints = (raw: string | null): string[] => {
		if (!raw) return [];

		const trimmed = raw.trim();
		if (!trimmed) return [];

		const variants = new Set<string>();
		variants.add(trimmed);

		// Remove surrounding parentheses if present
		if (trimmed.startsWith('(') && trimmed.endsWith(')') && trimmed.length > 2) {
			variants.add(trimmed.slice(1, -1));
		}

		// If prefixed with letters like p25 or page25
		const alphaNumeric = trimmed.replace(/^[^0-9]+/, '');
		if (alphaNumeric && alphaNumeric !== trimmed) {
			variants.add(alphaNumeric);
		}

		// Extract all numeric groups
		const numericMatches = trimmed.match(/\d+/g);
		numericMatches?.forEach((match) => {
			variants.add(match);
			variants.add(String(Number(match)));
		});

		return Array.from(variants).filter((value) => value.length > 0);
	};

	const splitDisplayHints = (raw: string | null): string[] => {
		if (!raw) return [];

		return raw
			.split(/(?:,|\/|;|\band\b)/gi)
			.map((value) => value.trim())
			.filter((value) => value.length > 0);
	};

	$: pageHint = (() => {
		const raw = attributes['data-page'];
		if (!raw) return null;
		try {
			return decodeURIComponent(raw).trim();
		} catch (e) {
			return raw.trim();
		}
	})();
	$: displayHints = splitDisplayHints(pageHint);
	$: citationIndex = (() => {
		const idx = Number(attributes?.data);
		if (Number.isNaN(idx) || idx <= 0) return null;
		return idx;
	})();
	const resolvePageTarget = (hint: string | null | undefined, entry: CitationLinkTarget | undefined) => {
		if (!hint || !entry?.pageTargets) return null;

		const candidates = derivePageHints(hint);
		for (const candidate of candidates) {
			const target = entry.pageTargets[candidate];
			if (target) {
				return target;
			}
		}

		return null;
	};

	$: targetUrl = (() => {
		if (!citationIndex) return null;
		const entry = sourceTargets?.[citationIndex - 1];
		if (!entry) return null;

		return resolvePageTarget(pageHint, entry) ?? entry.defaultTarget ?? null;
	})();
	$: pageLinks = (() => {
		if (!citationIndex) return [];
		const entry = sourceTargets?.[citationIndex - 1];
		if (!entry) return [];

		return displayHints.map((label) => ({
			label,
			url: resolvePageTarget(label, entry) ?? entry.defaultTarget ?? null
		}));
	})();
	$: displayLabel = (() => {
		const base = citationIndex ? `†${citationIndex}` : '†';
		return base;
	})();
</script>

{#if displayLabel}
	<span class="inline-flex flex-wrap items-center gap-1 text-xs font-medium translate-y-[2px] px-2 py-0.5 dark:bg-white/5 dark:text-white/60 dark:hover:text-white bg-gray-50 text-black/60 hover:text-black transition rounded-lg">
		{#if targetUrl}
			<a
				class="whitespace-nowrap underline-offset-2 hover:underline"
				href={targetUrl}
				target="_blank"
				title={decodedTitle ? getDisplayTitle(formattedTitle(decodedTitle)) : undefined}
				rel="noopener noreferrer"
			>
				{displayLabel}
			</a>
		{:else}
			<button
				class="whitespace-nowrap underline-offset-2 hover:underline"
				title={decodedTitle ? getDisplayTitle(formattedTitle(decodedTitle)) : undefined}
				on:click={() => {
					onClick(id, attributes.data, decodedTitle);
				}}
			>
				{displayLabel}
			</button>
		{/if}

		{#if pageLinks.length > 0}
			<span>(</span>
			{#each pageLinks as page, pageIdx}
				{#if page.url}
					<a
						class="whitespace-nowrap underline-offset-2 hover:underline"
						href={page.url}
						target="_blank"
						rel="noopener noreferrer"
						title={`Page ${page.label}`}
					>
						{page.label}
					</a>
				{:else}
					<button
						class="whitespace-nowrap underline-offset-2 hover:underline"
						on:click={() => {
							onClick(id, attributes.data, decodedTitle);
						}}
					>
						{page.label}
					</button>
				{/if}
				{#if pageIdx < pageLinks.length - 1}
					<span>,</span>
				{/if}
			{/each}
			<span>)</span>
		{/if}
	</span>
{/if}
