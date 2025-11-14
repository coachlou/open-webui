import { describe, expect, it } from 'vitest';
import { replaceTokens } from '../index';

const extractGroupPayload = (markup: string) => {
	const match = markup.match(/<source_group data="([^"]+)"/);
	expect(match).toBeTruthy();
	return JSON.parse(decodeURIComponent(match![1]));
};

describe('replaceTokens grouped citations', () => {
	it('parses explicit source references', () => {
		const result = replaceTokens('†(1:p4-11, 2:p17)', ['Doc 1', 'Doc 2'], 'char', 'user');
		const payload = extractGroupPayload(result);
		expect(payload).toEqual([
			{ index: 1, pages: ['p4-11'] },
			{ index: 2, pages: ['p17'] }
		]);
	});

	it('inherits the dagger index when omitted inside parentheses', () => {
		const result = replaceTokens('†1(p15-16,p20)', ['Doc 1'], 'char', 'user');
		const payload = extractGroupPayload(result);
		expect(payload).toEqual([{ index: 1, pages: ['p15-16', 'p20'] }]);
	});

	it('ignores references to non-existent sources', () => {
		const result = replaceTokens('†(4:p10)', ['Doc 1', 'Doc 2', 'Doc 3'], 'char', 'user');
		expect(result).not.toContain('<source_group');
	});

	it('filters out line numbers from citations', () => {
		const result = replaceTokens('†(1:p27, line 4)', ['Doc 1'], 'char', 'user');
		const payload = extractGroupPayload(result);
		expect(payload).toEqual([{ index: 1, pages: ['p27'] }]);
	});

	it('filters out multiple line numbers', () => {
		const result = replaceTokens('†(1:p25, lines 14)', ['Doc 1'], 'char', 'user');
		const payload = extractGroupPayload(result);
		expect(payload).toEqual([{ index: 1, pages: ['p25'] }]);
	});
});
