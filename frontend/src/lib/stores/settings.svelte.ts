export type CardVariant    = 'default';
export type CardSize       = 'small' | 'medium' | 'large' | 'xl';
export type TeaserMode     = 'sprite' | 'video';
export type ResultsPerPage = 4 | 8 | 16 | 24 | 36;

function createSettings() {
    let cardVariant = $state<CardVariant>(
        (localStorage.getItem('cardVariant') as CardVariant) ?? 'default'
    );
    let cardSize = $state<CardSize>(
        (localStorage.getItem('cardSize') as CardSize) ?? 'medium'
    );
    let teaserMode = $state<TeaserMode>(
        (localStorage.getItem('teaserMode') as TeaserMode) ?? 'sprite'
    );
    let resultsPerPage = $state<ResultsPerPage>(
        (parseInt(localStorage.getItem('searchResultsPerPage') ?? '24', 10) as ResultsPerPage) ?? 24
    );
    let devMode = $state<boolean>(
        localStorage.getItem('devMode') === 'true'
    );
    let focusMode = $state<boolean>(
        localStorage.getItem('focusMode') === 'true'
    );
    return {
        get cardVariant() { return cardVariant; },
        set cardVariant(v: CardVariant) { cardVariant = v; localStorage.setItem('cardVariant', v); },
        get cardSize() { return cardSize; },
        set cardSize(v: CardSize) { cardSize = v; localStorage.setItem('cardSize', v); },
        get teaserMode() { return teaserMode; },
        set teaserMode(v: TeaserMode) { teaserMode = v; localStorage.setItem('teaserMode', v); },
        get resultsPerPage() { return resultsPerPage; },
        set resultsPerPage(v: ResultsPerPage) { resultsPerPage = v; localStorage.setItem('searchResultsPerPage', String(v)); },
        get devMode() { return devMode; },
        set devMode(v: boolean) { devMode = v; localStorage.setItem('devMode', String(v)); },
        get devParam() { return devMode ? '?dev=true' : ''; },
        get focusMode() { return focusMode; },
        set focusMode(v: boolean) { focusMode = v; localStorage.setItem('focusMode', String(v)); },
    };
}

export const settings = createSettings();
