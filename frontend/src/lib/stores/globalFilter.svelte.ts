export interface GlobalFilter {
    collection: string;
    studio:     string;
    actors:     string[];
}

const EMPTY: GlobalFilter = { collection: '', studio: '', actors: [] };

function createStore() {
    let filter = $state<GlobalFilter>({ ...EMPTY });

    return {
        get current()  { return filter; },
        get isActive() { return filter.collection !== '' || filter.studio !== '' || filter.actors.length > 0; },
        set(f: GlobalFilter) { filter = f; },
        clear()        { filter = { ...EMPTY }; },
    };
}

export const globalFilter = createStore();
