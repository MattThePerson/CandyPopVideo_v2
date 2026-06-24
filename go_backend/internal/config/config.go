package config

import (
    _ "embed"
    "fmt"
    "os"
    "path/filepath"
    "sync"

    "gopkg.in/yaml.v3"
)

//go:embed default_config.yaml
var DefaultConfigBytes []byte

type CuratedQuery struct {
    SearchString   string   `yaml:"search_string"  json:"search_string,omitempty"`
    Actor          string   `yaml:"actor"          json:"actor,omitempty"`
    Studio         string   `yaml:"studio"         json:"studio,omitempty"`
    Collection     string   `yaml:"collection"     json:"collection,omitempty"`
    Tags           []string `yaml:"tags"           json:"tags,omitempty"`
    IncludeTerms   []string `yaml:"include_terms"  json:"include_terms,omitempty"`
    ExcludeTerms   []string `yaml:"exclude_terms"  json:"exclude_terms,omitempty"`
    OnlyFavourites string   `yaml:"only_favourites" json:"only_favourites,omitempty"`
    SortBy         string   `yaml:"sortby"         json:"sortby,omitempty"`
}

type CuratedCollection struct {
    Name        string       `yaml:"name"        json:"name"`
    Description string       `yaml:"description"  json:"description"`
    Query       CuratedQuery `yaml:"query"        json:"query"`
}

type Config struct {
    PreviewMediaDir      string              `yaml:"preview_media_dir"`
    DBBackupDir          string              `yaml:"db_backup"`
    DatetimeFormats      string              `yaml:"datetime_format"`
    SubtitleFolders      []string            `yaml:"subtitle_folders"`
    Collections          map[string][]string `yaml:"collections"`
    VideoExtensions      []string            `yaml:"video_extensions"`
    SceneFilenameFormats []string            `yaml:"scene_filename_formats"`
    CuratedCollections   []CuratedCollection `yaml:"curated_collections"`

    // derived from OS — never in config.yaml
    AppDataDir          string
    DBPath              string
    TfidfModelPath      string
    TfidfMatrixPath     string
    ActorProfilesPath   string
    StudioProfilesPath  string
    ActorInfoDir        string
}

// GetAppDataDir returns the OS-determined app data directory.
func GetAppDataDir() (string, error) {
    base, err := os.UserConfigDir()
    if err != nil {
        return "", fmt.Errorf("cannot determine user config dir: %w", err)
    }
    return filepath.Join(base, "CandyPopVideo"), nil
}

func deriveFields(c *Config, appDataDir string) {
    c.AppDataDir         = appDataDir
    c.DBPath             = filepath.Join(appDataDir, "app.db")
    c.TfidfModelPath     = filepath.Join(appDataDir, "tdidf.pkl")
    c.TfidfMatrixPath    = filepath.Join(appDataDir, "tdidf_matrix.pkl")
    c.ActorProfilesPath  = filepath.Join(appDataDir, "actor_profiles.pkl")
    c.StudioProfilesPath = filepath.Join(appDataDir, "studio_profiles.pkl")
    c.ActorInfoDir       = filepath.Join(appDataDir, "actors")
}

func parseConfig(data []byte, appDataDir string) (Config, error) {
    var c Config
    if err := yaml.Unmarshal(data, &c); err != nil {
        return c, err
    }
    deriveFields(&c, appDataDir)
    return c, nil
}

// ─── ConfigStore ─────────────────────────────────────────────────────────────

type ConfigStore struct {
    mu         sync.RWMutex
    cfg        Config
    appDataDir string
}

// Current returns a point-in-time snapshot of the config.
func (s *ConfigStore) Current() Config {
    s.mu.RLock()
    defer s.mu.RUnlock()
    return s.cfg
}

// RawYAML reads the config file from disk and returns its contents.
func (s *ConfigStore) RawYAML() (string, error) {
    data, err := os.ReadFile(filepath.Join(s.appDataDir, "config.yaml"))
    if err != nil {
        return "", err
    }
    return string(data), nil
}

// WriteAndReload writes new YAML content to config.yaml, parses it, and
// hot-reloads the store. Returns requiresRestart=true if preview_media_dir changed.
func (s *ConfigStore) WriteAndReload(content []byte) (requiresRestart bool, err error) {
    if err := os.WriteFile(filepath.Join(s.appDataDir, "config.yaml"), content, 0644); err != nil {
        return false, fmt.Errorf("writing config: %w", err)
    }
    newCfg, err := parseConfig(content, s.appDataDir)
    if err != nil {
        return false, fmt.Errorf("parsing new config: %w", err)
    }
    s.mu.Lock()
    defer s.mu.Unlock()
    if newCfg.PreviewMediaDir != s.cfg.PreviewMediaDir {
        requiresRestart = true
    }
    s.cfg = newCfg
    return requiresRestart, nil
}

// ─── Constructor ─────────────────────────────────────────────────────────────

// NewConfigStore initialises the app data directory (first-run or existing),
// reads config.yaml, and returns the live config store.
// If appDataDirOverride is non-empty it is used as-is; otherwise the directory
// is derived from os.UserConfigDir().
func NewConfigStore(appDataDirOverride string) (*ConfigStore, error) {
    var dir string
    if appDataDirOverride != "" {
        dir = appDataDirOverride
    } else {
        var err error
        dir, err = GetAppDataDir()
        if err != nil {
            return nil, err
        }
    }

    configPath := filepath.Join(dir, "config.yaml")

    // First run: create directory and write default config.
    if _, err := os.Stat(dir); os.IsNotExist(err) {
        if err := os.MkdirAll(dir, 0700); err != nil {
            return nil, fmt.Errorf("creating app data dir: %w", err)
        }
        if err := os.WriteFile(configPath, DefaultConfigBytes, 0644); err != nil {
            return nil, fmt.Errorf("writing default config: %w", err)
        }
    }

    data, err := os.ReadFile(configPath)
    if err != nil {
        return nil, fmt.Errorf("reading config: %w", err)
    }

    cfg, err := parseConfig(data, dir)
    if err != nil {
        return nil, fmt.Errorf("parsing config: %w", err)
    }

    return &ConfigStore{cfg: cfg, appDataDir: dir}, nil
}
