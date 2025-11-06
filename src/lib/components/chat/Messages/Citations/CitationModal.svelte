<script lang="ts">
	import { getContext, onMount, tick } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';

	import XMark from '$lib/components/icons/XMark.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let citation;
	export let showPercentage = false;
	export let showRelevance = true;

	let mergedDocuments = [];

	function calculatePercentage(distance: number) {
		if (typeof distance !== 'number') return null;
		if (distance < 0) return 0;
		if (distance > 1) return 100;
		return Math.round(distance * 10000) / 100;
	}

	function getRelevanceColor(percentage: number) {
		if (percentage >= 80)
			return 'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200';
		if (percentage >= 60)
			return 'bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200';
		if (percentage >= 40)
			return 'bg-orange-200 dark:bg-orange-800 text-orange-800 dark:text-orange-200';
		return 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200';
	}

	$: if (citation) {
		mergedDocuments =
			citation.document?.map((c, i) => {
				return {
					source: citation.source,
					document: c,
					metadata: citation.metadata?.[i],
					distance: citation.distances?.[i]
				};
			}) ?? [];

		mergedDocuments = mergedDocuments.sort((a, b) => {
			const pageA =
				typeof a?.metadata?.page === 'number' && !Number.isNaN(a.metadata.page)
					? a.metadata.page
					: undefined;
			const pageB =
				typeof b?.metadata?.page === 'number' && !Number.isNaN(b.metadata.page)
					? b.metadata.page
					: undefined;

			if (pageA !== undefined && pageB !== undefined) {
				return pageA - pageB;
			}
			if (pageA !== undefined) return -1;
			if (pageB !== undefined) return 1;

			const distA = a.distance ?? -Infinity;
			const distB = b.distance ?? -Infinity;
			return distB - distA;
		});
	} else {
		mergedDocuments = [];
	}

	const decodeString = (str: string) => {
		try {
			return decodeURIComponent(str);
		} catch (e) {
			return str;
		}
	};

	const getDocumentLink = (doc) => {
		if (!doc) return null;
		const page =
			typeof doc?.metadata?.page === 'number' && !Number.isNaN(doc.metadata.page)
				? doc.metadata.page + 1
				: undefined;

		if (doc?.metadata?.file_id) {
			return `${WEBUI_API_BASE_URL}/files/${doc.metadata.file_id}/content${
				page ? `#page=${page}` : ''
			}`;
		}

		if (doc?.source?.url && doc.source.url.startsWith('http')) {
			return doc.source.url;
		}

		return null;
	};
</script>

<Modal size="lg" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-4.5 pt-3 pb-2">
			<div class=" text-lg font-medium self-center flex items-center">
				{#if citation?.source?.name}
					{@const document = mergedDocuments?.[0]}
					{#if document?.metadata?.file_id || document.source?.url?.includes('http')}
						<Tooltip
							className="w-fit"
							content={document.source?.url?.includes('http')
								? $i18n.t('Open link')
								: $i18n.t('Open file')}
							placement="top-start"
							tippyOptions={{ duration: [500, 0] }}
						>
							<a
								class="hover:text-gray-500 dark:hover:text-gray-100 underline grow line-clamp-1"
								href={document?.metadata?.file_id
									? `${WEBUI_API_BASE_URL}/files/${document?.metadata?.file_id}/content${document?.metadata?.page !== undefined ? `#page=${document.metadata.page + 1}` : ''}`
									: document.source?.url?.includes('http')
										? document.source.url
										: `#`}
								target="_blank"
							>
								{decodeString(citation?.source?.name)}
							</a>
						</Tooltip>
					{:else}
						{decodeString(citation?.source?.name)}
					{/if}
				{:else}
					{$i18n.t('Citation')}
				{/if}
			</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<XMark className={'size-5'} />
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full px-5 pb-5 md:space-x-4">
			<div
				class="flex flex-col w-full dark:text-gray-200 overflow-y-scroll max-h-[22rem] scrollbar-thin gap-1"
			>
				{#each mergedDocuments as document, documentIdx}
					{@const pageLink = getDocumentLink(document)}
					{@const pageDisplay =
						typeof document?.metadata?.page === 'number' && !Number.isNaN(document.metadata.page)
							? document.metadata.page + 1
							: null}
					<div class="flex flex-col w-full gap-3 rounded-lg border border-gray-200/70 dark:border-gray-800 bg-gray-50/80 dark:bg-gray-900/40 p-3">
						{#if document.metadata?.parameters}
							<div>
								<div class="text-sm font-medium dark:text-gray-300 mb-1">
									{$i18n.t('Parameters')}
								</div>

								<Textarea readonly value={JSON.stringify(document.metadata.parameters, null, 2)}
								></Textarea>
							</div>
						{/if}

						<div class="flex flex-col gap-2">
							<header class="flex flex-wrap items-center justify-between gap-2">
								<div class="text-sm font-semibold text-gray-700 dark:text-gray-200">
									{decodeString(citation?.source?.name)}
								</div>

								<div class="flex items-center gap-2 text-xs">
									{#if pageDisplay}
										{#if pageLink}
											<a
												class="inline-flex items-center gap-1 font-medium text-emerald-600 hover:text-emerald-500 underline decoration-dotted hover:decoration-solid"
												href={pageLink}
												target="_blank"
												rel="noopener noreferrer"
											>
												{$i18n.t('Page')} {pageDisplay}
												<span aria-hidden="true">↗</span>
											</a>
										{:else}
											<span class="font-medium text-gray-500 dark:text-gray-400">
												{$i18n.t('Page')} {pageDisplay}
											</span>
										{/if}
									{/if}

									{#if showRelevance && document.distance !== undefined}
										<Tooltip
											className="w-fit"
											content={$i18n.t('Relevance')}
											placement="top-start"
											tippyOptions={{ duration: [500, 0] }}
										>
											{#if showPercentage}
												{@const percentage = calculatePercentage(document.distance)}
												{#if typeof percentage === 'number'}
													<span
														class={`px-1.5 py-0.5 rounded-md text-[0.65rem] font-semibold ${getRelevanceColor(
															percentage
														)}`}
													>
														{percentage.toFixed(1)}%
													</span>
												{/if}
											{:else if typeof document?.distance === 'number'}
												<span class="text-xs text-gray-400 dark:text-gray-500">
													{(document?.distance ?? 0).toFixed(4)}
												</span>
											{/if}
										</Tooltip>
									{/if}
								</div>
							</header>

							{#if document.metadata?.html}
								<iframe
									class="w-full border border-gray-200 dark:border-gray-800 rounded-md"
									sandbox="allow-scripts allow-forms allow-same-origin"
									srcdoc={document.document}
									title={$i18n.t('Content')}
								></iframe>
							{:else}
								<div class="prose prose-sm dark:prose-invert max-w-none bg-white/80 dark:bg-gray-900/60 border border-gray-200 dark:border-gray-800 rounded-md p-3">
									<p class="whitespace-pre-line">{document.document}</p>
								</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
</Modal>
