<script lang="ts">
	export let id;
	export let token;
	export let onClick: Function = () => {};

	let attributes: Record<string, string | undefined> = {};

	function extractAttributes(input: string): Record<string, string> {
		const regex = /([a-zA-Z0-9-]+)="([^"]*)"/g;
		let match;
		let attrs: Record<string, string> = {};

		while ((match = regex.exec(input)) !== null) {
			attrs[match[1]] = match[2];
		}

		return attrs;
	}

	$: attributes = extractAttributes(token.text);

	$: href =
		attributes['data-href'] && attributes['data-href'] !== 'undefined'
			? decodeURIComponent(attributes['data-href'])
			: null;

	$: indexLabel = attributes.data ?? attributes['data'] ?? '?';

	$: pageNumber =
		attributes['data-page'] !== undefined && attributes['data-page'] !== null
			? Number(attributes['data-page'])
			: undefined;

	$: pageDisplay =
		Number.isFinite(pageNumber) && !Number.isNaN(pageNumber) ? pageNumber + 1 : undefined;

	$: titleText =
		attributes.title && attributes.title !== 'N/A'
			? decodeURIComponent(attributes.title)
			: '';

	$: displayLabel = `[${indexLabel}${pageDisplay !== undefined ? `(${pageDisplay})` : ''}]`;
</script>

{#if href}
	<a
		class="text-xs font-medium inline-flex items-center text-emerald-500 hover:text-emerald-600 underline decoration-dotted hover:decoration-solid transition"
		href={href}
		target="_blank"
		rel="noopener noreferrer"
		title={titleText || undefined}
	>
		{displayLabel}
	</a>
{:else}
	<button
		class="text-xs font-medium inline-flex items-center text-emerald-500 hover:text-emerald-600 underline decoration-dotted hover:decoration-solid transition bg-transparent px-1 py-0"
		on:click={() => {
			onClick(id, attributes.data);
		}}
		title={titleText || undefined}
	>
		{displayLabel}
	</button>
{/if}
