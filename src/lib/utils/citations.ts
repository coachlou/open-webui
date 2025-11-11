import { WEBUI_API_BASE_URL } from '$lib/constants';

const HTTP_PROTOCOL_REGEX = /^https?:\/\//i;

export interface CitationMetadata {
	[key: string]: any;
}

export interface NormalizedCitation {
	id: string;
	displayName: string;
	source: Record<string, any>;
	document: any[];
	metadata: (CitationMetadata | undefined)[];
	distances?: number[];
}

export interface PageInfo {
	display: string | null;
	anchor: number | null;
}

const isHttpUrl = (value?: unknown): value is string =>
	typeof value === 'string' && HTTP_PROTOCOL_REGEX.test(value);

export const normalizeCitations = (rawSources: any[] = []): NormalizedCitation[] => {
	const citations: NormalizedCitation[] = [];
	let fallbackCounter = 0;

	for (const sourceEntry of rawSources ?? []) {
		if (!sourceEntry || typeof sourceEntry !== 'object') continue;

		const documents = Array.isArray(sourceEntry.document) ? sourceEntry.document : [];
		const metadatas = Array.isArray(sourceEntry.metadata) ? sourceEntry.metadata : [];
		const distances = Array.isArray(sourceEntry.distances) ? sourceEntry.distances : [];

		documents.forEach((document, index) => {
			const metadata = metadatas[index];
			const distance = distances[index];
			const candidateId =
				metadata?.source ??
				metadata?.file_id ??
				sourceEntry?.source?.id ??
				`source-${fallbackCounter++}`;

			const normalizedId =
				typeof candidateId === 'string' ? candidateId : String(candidateId ?? `source-${fallbackCounter++}`);

			let normalizedSource =
				sourceEntry?.source && typeof sourceEntry.source === 'object'
					? { ...sourceEntry.source }
					: {};

			if (metadata?.name) {
				normalizedSource = { ...normalizedSource, name: metadata.name };
			}

			if (isHttpUrl(normalizedId)) {
				normalizedSource = { ...normalizedSource, name: normalizedId, url: normalizedId };
			}

			const displayName =
				(typeof metadata?.name === 'string' && metadata.name.trim() !== ''
					? metadata.name
					: typeof normalizedSource?.name === 'string'
						? normalizedSource.name
						: normalizedId) || 'N/A';

			const existing = citations.find((entry) => entry.id === normalizedId);

			if (existing) {
				existing.document.push(document);
				existing.metadata.push(metadata);
				if (typeof distance === 'number') {
					if (!existing.distances) existing.distances = [];
					existing.distances.push(distance);
				}
			} else {
				citations.push({
					id: normalizedId,
					displayName,
					source:
						Object.keys(normalizedSource).length > 0
							? normalizedSource
							: {
									name: displayName
							  },
					document: [document],
					metadata: [metadata],
					distances: typeof distance === 'number' ? [distance] : undefined
				});
			}
		});
	}

	return citations;
};

export const extractPageInfo = (metadata?: CitationMetadata | null): PageInfo => {
	if (!metadata || typeof metadata !== 'object') {
		return { display: null, anchor: null };
	}

	const labelCandidates = [
		metadata.page_label,
		metadata.pageLabel,
		metadata.page_name,
		metadata.pageName
	];

	for (const label of labelCandidates) {
		if (label === undefined || label === null) continue;
		if (typeof label === 'number' && !Number.isNaN(label)) {
			return { display: String(label), anchor: Number(label) };
		}
		if (typeof label === 'string' && label.trim().length > 0) {
			const parsed = Number(label);
			return {
				display: label,
				anchor: Number.isNaN(parsed) ? null : parsed
			};
		}
	}

	const numericFields: { key: string; adjust: number }[] = [
		{ key: 'page_number', adjust: 0 },
		{ key: 'page_num', adjust: 0 },
		{ key: 'page', adjust: 1 }
	];

	for (const { key, adjust } of numericFields) {
		const value = metadata[key];

		if (typeof value === 'number' && !Number.isNaN(value)) {
			const anchor = value + adjust;
			return {
				display: String(anchor),
				anchor
			};
		}

		if (typeof value === 'string' && value.trim().length > 0) {
			const parsed = Number(value);
			if (!Number.isNaN(parsed)) {
				const anchor = parsed + adjust;
				return {
					display: String(anchor),
					anchor
				};
			}
		}
	}

	return { display: null, anchor: null };
};

export const buildDocumentUrl = (
	metadata?: CitationMetadata | null,
	source?: Record<string, any>
): string | null => {
	if (metadata?.file_id) {
		const pageInfo = extractPageInfo(metadata);
		const anchor = pageInfo.anchor ? `#page=${pageInfo.anchor}` : '';
		return `${WEBUI_API_BASE_URL}/files/${metadata.file_id}/content${anchor}`;
	}

	if (source?.url && isHttpUrl(source.url)) {
		return source.url;
	}

	if (source?.embed_url && isHttpUrl(source.embed_url)) {
		return source.embed_url;
	}

	return null;
};
