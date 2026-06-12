export interface CatalogSymbol {
  id: string
  code: string
  name: string
  category: string
  categoryLabel: string
  file: string
  color: string
  placeholder?: boolean
}

export interface Catalog {
  symbols: CatalogSymbol[]
}

export type ToolName = 'select' | 'pen' | 'symbol' | 'text'
