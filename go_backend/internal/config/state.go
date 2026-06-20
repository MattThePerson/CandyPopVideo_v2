package config

import (
    "encoding/json"
    "os"
    "path/filepath"
    "sync"
)

type GlobalFilter struct {
    Collection string   `json:"collection"`
    Studio     string   `json:"studio"`
    Actors     []string `json:"actors"`
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
    if s.state.GlobalFilter.Actors == nil {
        s.state.GlobalFilter.Actors = []string{}
    }
    return s
}

func (s *AppStateStore) GetFilter() GlobalFilter {
    s.mu.RLock()
    defer s.mu.RUnlock()
    f := s.state.GlobalFilter
    if f.Actors == nil {
        f.Actors = []string{}
    }
    return f
}

func (s *AppStateStore) SetFilter(f GlobalFilter) error {
    if f.Actors == nil {
        f.Actors = []string{}
    }
    s.mu.Lock()
    s.state.GlobalFilter = f
    data, err := json.MarshalIndent(s.state, "", "    ")
    s.mu.Unlock()
    if err != nil {
        return err
    }
    return os.WriteFile(s.path, data, 0644)
}
