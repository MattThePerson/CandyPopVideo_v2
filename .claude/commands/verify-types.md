Audit that the Go schemas and TypeScript interfaces are in sync.

The Go source of truth is in go_backend/internal/schemas/ (VideoData, VideoInteractions, SearchQuery, CatalogueQuery).
The TypeScript mirror is in frontend/src/lib/types/ (video.ts, query.ts).

Steps:
1. Read all Go struct definitions in go_backend/internal/schemas/.
2. Read all TypeScript interfaces in frontend/src/lib/types/.
3. For each field in each Go struct, verify the TypeScript interface has a matching field with a compatible type. Pay attention to:
   - Field name casing (Go uses PascalCase exported fields with json tags; TS uses camelCase matching the json tag)
   - Type mapping: Go string→TS string, bool→boolean, int/float64→number, []T→T[], map[string]T→Record<string,T> or similar
   - Optional fields: Go pointer types (*T) or fields that may be zero-valued should be optional (?) in TypeScript
   - Fields present in Go but missing from TypeScript (frontend will silently ignore them — flag these)
   - Fields present in TypeScript but not in Go (frontend may break if it expects data that never arrives — flag these)
4. Report all mismatches, missing fields, and type incompatibilities. If everything matches, say so explicitly.
5. Do NOT auto-fix mismatches — report them and let the user decide which side to update.
