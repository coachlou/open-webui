<script lang="ts">
	export let id;
	export let token;
	export let onClick: Function = () => {};
	export let sourceTargets: (string | null | undefined)[] = [];

	let attributes: Record<string, string | undefined> = {};
	let decodedTitle: string | undefined;
	let targetUrl: string | null = null;

	function extractAttributes(input: string): Record<string, string> {
		const regex = /(\w+)="([^"]*)"/g;
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
	$: targetUrl = (() => {
		const idx = Number(attributes?.data);
		if (Number.isNaN(idx) || idx <= 0) return null;
		return sourceTargets?.[idx - 1] ?? null;
	})();
</script>

{#if decodedTitle && decodedTitle !== 'N/A'}
	{#if targetUrl}
		<a
			class="text-xs font-medium w-fit translate-y-[2px] px-2 py-0.5 dark:bg-white/5 dark:text-white/60 dark:hover:text-white bg-gray-50 text-black/60 hover:text-black transition rounded-lg"
			href={targetUrl}
			target="_blank"
			rel="noopener noreferrer"
		>
			<span class="line-clamp-1">
				{getDisplayTitle(formattedTitle(decodedTitle))}
			</span>
		</a>
	{:else}
		<button
			class="text-xs font-medium w-fit translate-y-[2px] px-2 py-0.5 dark:bg-white/5 dark:text-white/60 dark:hover:text-white bg-gray-50 text-black/60 hover:text-black transition rounded-lg"
			on:click={() => {
				onClick(id, attributes.data, decodedTitle);
			}}
		>
			<span class="line-clamp-1">{getDisplayTitle(formattedTitle(decodedTitle))}</span>
		</button>
	{/if}
{/if}
