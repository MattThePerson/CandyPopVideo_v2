import type { Component } from 'svelte';
import HomePage from '../../pages/home/Page.svelte';
import SearchPage from '../../pages/search/Page.svelte';
import CataloguePage from '../../pages/catalogue/Page.svelte';
import CuratedPage from '../../pages/curated/Page.svelte';
import VideoPage from '../../pages/video/Page.svelte';
import DashboardPage from '../../pages/dashboard/Page.svelte';
import ConfigPage from '../../pages/config/Page.svelte';
import HistoryPage from '../../pages/history/Page.svelte';

export interface RouteDef {
    pattern: string;
    component: Component;
}

// Checked in order, first match wins -- keep more specific patterns
// (e.g. '/video/:hash') above less specific ones once those exist.
export const routes: RouteDef[] = [
    { pattern: '/', component: HomePage },
    { pattern: '/search', component: SearchPage },
    { pattern: '/catalogue', component: CataloguePage },
    { pattern: '/curated', component: CuratedPage },
    { pattern: '/video/:hash', component: VideoPage },
    { pattern: '/history', component: HistoryPage },
    { pattern: '/dashboard', component: DashboardPage },
    { pattern: '/config', component: ConfigPage },
];
