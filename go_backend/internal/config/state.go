package config

import (
    "encoding/json"
    "os"
    "path/filepath"
    "sync"
)

type GlobalFilter struct {
    CollectionsInclude []string `json:"collections_include"`
    CollectionsExclude []string `json:"collections_exclude"`
    CollectionsMode    string   `json:"collections_mode"` // "include" | "exclude"
    StudiosInclude     []string `json:"studios_include"`
    StudiosExclude     []string `json:"studios_exclude"`
    StudiosMode        string   `json:"studios_mode"` // "include" | "exclude"
    ActorsInclude      []string `json:"actors_include"`
    ActorsExclude      []string `json:"actors_exclude"`
}

type appState struct {
    GlobalFilter GlobalFilter `json:"global_filter"`
}

// AppStateStore persists transient app state (e.g. global content filter) to state.json.
type AppStateStore struct {
    mu    sync.RWMutex
    state appState
    path  string
}

// NewAppStateStore loads state.json from appDataDir (or starts with defaults on missing/corrupt file).
func NewAppStateStore(appDataDir string) *AppStateStore {
    s := &AppStateStore{path: filepath.Join(appDataDir, "state.json")}
    if data, err := os.ReadFile(s.path); err == nil {
        json.Unmarshal(data, &s.state) //nolint — default zero state on bad JSON is intentional
    }
    initFilterSlices(&s.state.GlobalFilter)
    return s
}

func (s *AppStateStore) GetFilter() GlobalFilter {
    s.mu.RLock()
    defer s.mu.RUnlock()
    f := s.state.GlobalFilter
    initFilterSlices(&f)
    return f
}

func (s *AppStateStore) SetFilter(f GlobalFilter) error {
    initFilterSlices(&f)
    s.mu.Lock()
    s.state.GlobalFilter = f
    data, err := json.MarshalIndent(s.state, "", "    ")
    s.mu.Unlock()
    if err != nil {
        return err
    }
    return os.WriteFile(s.path, data, 0644)
}

// initFilterSlices ensures no nil slices are serialised as JSON null.
func initFilterSlices(f *GlobalFilter) {
    if f.CollectionsInclude == nil { f.CollectionsInclude = []string{} }
    if f.CollectionsExclude == nil { f.CollectionsExclude = []string{} }
    if f.StudiosInclude     == nil { f.StudiosInclude     = []string{} }
    if f.StudiosExclude     == nil { f.StudiosExclude     = []string{} }
    if f.ActorsInclude      == nil { f.ActorsInclude      = []string{} }
    if f.ActorsExclude      == nil { f.ActorsExclude      = []string{} }
}
