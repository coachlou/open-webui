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
	let pageRangeLabel = '';
	let titleDocument = null;
	let titleUrl: string | null = null;

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

	function getDocumentUrl(document) {
		if (!document) return null;

		const fileId = document?.metadata?.file_id;
		const hasPageNumber = Number.isInteger(document?.metadata?.page);
		const pageSuffix = hasPageNumber ? `#page=${document.metadata.page + 1}` : '';

		if (fileId) {
			return `${WEBUI_API_BASE_URL}/files/${fileId}/content${pageSuffix}`;
		}

		if (document?.source?.url?.startsWith('http')) {
			return `${document.source.url}${hasPageNumber ? pageSuffix : ''}`;
		}

		return null;
	}

	$: if (citation) {
		const mappedDocuments =
			citation.document?.map((c, i) => {
				const metadata = citation.metadata?.[i];
				const pageNumber = Number.isInteger(metadata?.page) ? metadata.page : null;

				return {
					source: citation.source,
					document: c,
					metadata,
					distance: citation.distances?.[i],
					pageNumber,
					index: i
				};
			}) ?? [];

		const documentsWithPages = mappedDocuments.filter((doc) => doc.pageNumber !== null);

		mergedDocuments = mappedDocuments
			.slice()
			.sort((a, b) => {
				if (a.pageNumber !== null && b.pageNumber !== null && a.pageNumber !== b.pageNumber) {
					return a.pageNumber - b.pageNumber;
				}
				if (a.pageNumber !== null && b.pageNumber === null) return -1;
				if (a.pageNumber === null && b.pageNumber !== null) return 1;
				return a.index - b.index;
			})
			.map(({ index, ...doc }) => doc);

		if (documentsWithPages.length) {
			const sortedPages = documentsWithPages
				.map((doc) => doc.pageNumber ?? 0)
				.sort((a, b) => a - b);
			const first = sortedPages[0];
			const last = sortedPages[sortedPages.length - 1];
			pageRangeLabel = first === last ? `${first + 1}` : `${first + 1}–${last + 1}`;
		} else {
			pageRangeLabel = '';
		}

		titleDocument =
			mergedDocuments.find(
				(doc) => doc?.metadata?.file_id || doc?.source?.url?.startsWith?.('http')
			) ?? mergedDocuments[0] ?? null;

		titleUrl = getDocumentUrl(titleDocument);
	} else {
		mergedDocuments = [];
		pageRangeLabel = '';
		titleDocument = null;
		titleUrl = null;
	}

	const decodeString = (str: string) => {
		try {
			return decodeURIComponent(str);
		} catch (e) {
			return str;
		}
	};
</script>

<Modal size="lg" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-4.5 pt-3 pb-2">
			<div class="flex min-w-0 flex-col gap-0.5">
				{#if citation?.source?.name || mergedDocuments.length > 0}
					{@const citationTitle = decodeString(
						citation?.source?.name ??
							mergedDocuments?.[0]?.metadata?.name ??
							$i18n.t('Citation')
					)}
					{#if titleUrl}
						<Tooltip
							className="w-fit"
							content={$i18n.t('Open file')}
							placement="top-start"
							tippyOptions={{ duration: [500, 0] }}
						>
							<a
								class="text-lg font-medium hover:text-gray-500 dark:hover:text-gray-100 underline-offset-4 hover:underline line-clamp-1"
								href={titleUrl}
								target="_blank"
							>
								{citationTitle}
							</a>
						</Tooltip>
					{:else}
						<div class="text-lg font-medium line-clamp-2">{citationTitle}</div>
					{/if}
				{:else}
					<div class="text-lg font-medium">{$i18n.t('Citation')}</div>
				{/if}

				{#if pageRangeLabel}
					<div class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
						{$i18n.t('page')} {pageRangeLabel}
					</div>
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
				class="flex flex-col w-full dark:text-gray-200 overflow-y-scroll max-h-[22rem] scrollbar-thin gap-3"
			>
				{#if mergedDocuments.length === 0}
					<div class="rounded-xl border border-dashed border-gray-200 dark:border-gray-800 px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
						{$i18n.t('No sources available')}
					</div>
				{:else}
					{#each mergedDocuments as document}
						<article class="rounded-2xl border border-gray-100 bg-white/80 px-4 py-3 shadow-sm dark:border-gray-900 dark:bg-gray-950/40">
							<header class="flex flex-wrap items-center gap-2 text-sm font-medium text-gray-900 dark:text-gray-100">
								<span class="truncate">
									{decodeString(document.metadata?.name ?? document.source?.name ?? $i18n.t('Source'))}
								</span>
								<div class="ml-auto flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
									{#if Number.isInteger(document?.pageNumber)}
										<span>{$i18n.t('page')} {document.pageNumber + 1}</span>
									{/if}
									{#if getDocumentUrl(document)}
										<a
											class="inline-flex items-center gap-1 rounded-full border border-gray-200 px-2 py-0.5 text-[11px] font-semibold text-gray-600 transition hover:border-gray-300 hover:text-gray-900 dark:border-gray-800 dark:text-gray-300 dark:hover:text-gray-100"
											href={getDocumentUrl(document)}
											target="_blank"
										>
											{$i18n.t('Open')}
										</a>
									{/if}
								</div>
							</header>

							{#if document.metadata?.parameters}
								<div class="mt-3">
									<div class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
										{$i18n.t('Parameters')}
									</div>
									<Textarea readonly value={JSON.stringify(document.metadata.parameters, null, 2)}
									></Textarea>
								</div>
							{/if}

							{#if showRelevance}
								<div class="mt-3">
									<div class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
										{$i18n.t('Relevance')}
									</div>
									{#if document.distance !== undefined}
										<Tooltip
											className="w-fit"
											content={$i18n.t('Semantic distance to query')}
											placement="top-start"
											tippyOptions={{ duration: [500, 0] }}
										>
											<div class="mt-1 flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300">
												{#if showPercentage}
													{@const percentage = calculatePercentage(document.distance)}
													{#if typeof percentage === 'number'}
														<span
															class={`px-1.5 py-0.5 text-xs font-semibold ${getRelevanceColor(percentage)} rounded-md`}
														>
															{percentage.toFixed(2)}%
														</span>
													{/if}
													{#if typeof document?.distance === 'number'}
														<span class="text-xs text-gray-500 dark:text-gray-400">
															({(document?.distance ?? 0).toFixed(4)})
														</span>
													{/if}
												{:else if typeof document?.distance === 'number'}
													<span class="text-xs text-gray-500 dark:text-gray-400">
														({(document?.distance ?? 0).toFixed(4)})
													</span>
												{/if}
											</div>
										</Tooltip>
									{:else}
										<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
											{$i18n.t('No distance available')}
										</div>
									{/if}
								</div>
							{/if}

							<div class="mt-3">
								<div class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
									{$i18n.t('Content')}
								</div>
								{#if document.metadata?.html}
									<iframe
										class="mt-1 w-full rounded-lg border border-gray-100 dark:border-gray-800"
										sandbox="allow-scripts allow-forms allow-same-origin"
										srcdoc={document.document}
										title={$i18n.t('Content')}
									></iframe>
								{:else}
									<pre class="mt-1 whitespace-pre-line rounded-lg bg-gray-50 px-3 py-2 text-sm text-gray-700 dark:bg-gray-900 dark:text-gray-300">
										{document.document}
									</pre>
								{/if}
							</div>
						</article>
					{/each}
				{/if}
			</div>
		</div>
	</div>
</Modal>
