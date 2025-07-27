package main

import (
	"log"
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	AppDataDir      string   `yaml:"app_data_dir"`
	DatetimeFormats string   `yaml:"datetime_format"`
	SubtitleFolders []string `yaml:"subtitle_folders"`

	DBPath          string
	PreviewMediaDir string
	ActorInfoDir    string
}

// Get Config struct from .yaml file
func GetConfig(fn string) Config {

	// Read file
	data, err := os.ReadFile(fn)
	if err != nil {
		log.Fatal("Unable to read file: " + fn)
	}

	// Parse into Config
	c := Config{}

	if err := yaml.Unmarshal([]byte(data), &c); err != nil {
		log.Fatal("Unable to Unmarshal data to Config struct")
	}

	c.DBPath = 			c.AppDataDir + "/app.db"
	c.PreviewMediaDir = c.AppDataDir + "/media/preview"
	c.ActorInfoDir = 	c.AppDataDir + "/actors"

	return c

}
