export interface GlobalFilter {
    collections_include: string[];
    collections_exclude: string[];
    collections_mode:    string;   // "include" | "exclude"
    studios_include:     string[];
    studios_exclude:     string[];
    studios_mode:        string;
    actors_include:      string[];
    actors_exclude:      string[];
}

const EMPTY: GlobalFilter = {
    collections_include: [], collections_exclude: [], collections_mode: 'include',
    studios_include:     [], studios_exclude:     [], studios_mode:     'include',
    actors_include:      [], actors_exclude:      [],
};

function createStore() {
    let filter = $state<GlobalFilter>({ ...EMPTY });

    return {
        get current()  { return filter; },
        get isActive() {
            return filter.collections_include.length > 0 || filter.collections_exclude.length > 0 ||
                   filter.studios_include.length > 0     || filter.studios_exclude.length > 0     ||
                   filter.actors_include.length > 0      || filter.actors_exclude.length > 0;
        },
        set(f: GlobalFilter) { filter = f; },
        clear()        { filter = { ...EMPTY }; },
    };
}

export const globalFilter = createStore();
