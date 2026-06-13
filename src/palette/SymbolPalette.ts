import type { Catalog, CatalogSymbol } from '../types'

type OnSelectSymbol = (sym: CatalogSymbol) => void

export class SymbolPalette {
  private el: HTMLElement
  private catalog: Catalog | null = null
  private activeCategory = 'all'
  private onSelect: OnSelectSymbol

  constructor(containerId: string, onSelect: OnSelectSymbol) {
    this.el = document.getElementById(containerId)!
    this.onSelect = onSelect
  }

  async load() {
    try {
      const resp = await fetch('/assets/catalog.json')
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      this.catalog = await resp.json() as Catalog
      this.render()
    } catch (err) {
      console.error("Failed to load catalog:", err)
      this.el.innerHTML = '<p class="palette-error">Erro ao carregar catálogo de símbolos.</p>'
    }
  }

  private categories(): { id: string; label: string }[] {
    if (!this.catalog) return []
    const seen = new Map<string, string>()
    for (const s of this.catalog.symbols) {
      if (!seen.has(s.category)) seen.set(s.category, s.categoryLabel)
    }
    const priority = ['all', 'protecao', 'reuniao']
    const cats = [{ id: 'all', label: 'Todos' }, ...Array.from(seen, ([id, label]) => ({ id, label }))]
    cats.sort((a, b) => {
      const idxA = priority.indexOf(a.id)
      const idxB = priority.indexOf(b.id)
      if (idxA !== -1 && idxB !== -1) return idxA - idxB
      if (idxA !== -1) return -1
      if (idxB !== -1) return 1
      return a.label.localeCompare(b.label)
    })
    return cats
  }

  setCategory(catId: string) {
    this.activeCategory = catId
    this.render()
  }

  private render() {
    if (!this.catalog) return
    const cats = this.categories()
    const filtered = this.activeCategory === 'all'
      ? this.catalog.symbols
      : this.catalog.symbols.filter(s => s.category === this.activeCategory)

    this.el.innerHTML = `
      <div class="palette-filters">
        ${cats.map(c => `
          <button class="cat-btn ${c.id === this.activeCategory ? 'active' : ''}" data-cat="${c.id}">
            ${c.label}
          </button>`).join('')}
      </div>
      <div class="palette-grid">
        ${filtered.map(sym => `
          <button class="sym-btn" data-id="${sym.id}" title="${sym.name}\n${sym.code}">
            <img src="${sym.file}" alt="${sym.name}" width="40" height="40" />
            <span>${sym.name}</span>
          </button>`).join('')}
      </div>
    `

    this.el.querySelectorAll<HTMLButtonElement>('.cat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeCategory = btn.dataset.cat!
        this.render()
      })
    })

    this.el.querySelectorAll<HTMLButtonElement>('.sym-btn').forEach(btn => {
      const sym = this.catalog!.symbols.find(s => s.id === btn.dataset.id)
      if (!sym) return

      // Determine if it's a line tool (can't be dropped as a single symbol)
      const isLineTool = ['B3-a', 'B3-b', 'B3-c', 'B3-d', 'B6-d', 'b3-a', 'b3-b', 'b3-c', 'b3-d', 'b6-d'].includes(sym.code)

      if (!isLineTool) {
        btn.draggable = true
        btn.addEventListener('dragstart', (e) => {
          if (e.dataTransfer) {
            e.dataTransfer.setData('application/x-crocreate-symbol', sym.id)
            e.dataTransfer.effectAllowed = 'copy'
          }
        })
      }

      btn.addEventListener('click', () => {
        this.el.querySelectorAll('.sym-btn').forEach(b => b.classList.remove('selected'))
        btn.classList.add('selected')
        this.onSelect(sym)
      })
    })
  }

  clearSelection() {
    this.el.querySelectorAll('.sym-btn').forEach(b => b.classList.remove('selected'))
  }

  getSymbol(id: string): CatalogSymbol | undefined {
    return this.catalog?.symbols.find(s => s.id === id)
  }
}
