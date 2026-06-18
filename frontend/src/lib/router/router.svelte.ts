import { routes, type RouteDef } from './routes';

export const routerState = $state({ path: window.location.pathname, search: window.location.search });

export function navigate(fullPath: string, { replace = false }: { replace?: boolean } = {}) {
    const qIdx = fullPath.indexOf('?');
    const pathname = qIdx >= 0 ? fullPath.slice(0, qIdx) : fullPath;
    const search   = qIdx >= 0 ? fullPath.slice(qIdx)    : '';

    if (pathname === routerState.path && search === routerState.search) return;

    if (replace) {
        history.replaceState({}, '', fullPath);
    } else {
        history.pushState({}, '', fullPath);
    }
    routerState.path   = pathname;
    routerState.search = search;
}

function onPopState() {
    routerState.path   = window.location.pathname;
    routerState.search = window.location.search;
}

function isModifiedClick(e: MouseEvent) {
    return e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey;
}

function onDocumentClick(e: MouseEvent) {
    if (isModifiedClick(e)) return;

    const anchor = (e.target as Element)?.closest?.('a');
    if (!anchor) return;
    if (anchor.target && anchor.target !== '_self') return;
    if (anchor.hasAttribute('download')) return;

    const url = new URL(anchor.href, window.location.href);
    if (url.origin !== window.location.origin) return;

    e.preventDefault();
    navigate(url.pathname + url.search + url.hash);
}

export function initRouter() {
    window.addEventListener('popstate', onPopState);
    document.addEventListener('click', onDocumentClick);
    return () => {
        window.removeEventListener('popstate', onPopState);
        document.removeEventListener('click', onDocumentClick);
    };
}

export interface MatchResult {
    route: RouteDef;
    params: Record<string, string>;
}

function matchPattern(pattern: string, path: string): Record<string, string> | null {
    const patternParts = pattern.split('/').filter(Boolean);
    const pathParts = path.split('/').filter(Boolean);
    if (patternParts.length !== pathParts.length) return null;

    const params: Record<string, string> = {};
    for (let i = 0; i < patternParts.length; i++) {
        const part = patternParts[i];
        if (part.startsWith(':')) {
            params[part.slice(1)] = decodeURIComponent(pathParts[i]);
        } else if (part !== pathParts[i]) {
            return null;
        }
    }
    return params;
}

export function matchRoute(path: string): MatchResult | null {
    for (const route of routes) {
        const params = matchPattern(route.pattern, path);
        if (params) return { route, params };
    }
    return null;
}
