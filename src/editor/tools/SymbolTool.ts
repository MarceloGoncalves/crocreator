import paper from 'paper'
import type { CatalogSymbol } from '../../types'
import type { History } from '../History'

export class SymbolTool {
  private tool: paper.Tool
  private currentSymbol: CatalogSymbol | null = null
  private symbolDefs = new Map<string, paper.SymbolDefinition>()
  private history: History
  private onChanged: () => void

  constructor(history: History, onChanged: () => void) {
    this.history = history
    this.onChanged = onChanged
    this.tool = new paper.Tool()

    this.tool.onMouseDown = async (event: paper.ToolEvent) => {
      if (!this.currentSymbol) return
      await this.insertSymbolAt(this.currentSymbol, event.point)
    }
  }

  async insertSymbolAt(sym: CatalogSymbol, point: paper.Point) {
    const def = await this.getOrLoadDef(sym)
    if (!def) return

    const item = new paper.SymbolItem(def, point)
    
    // Normaliza o tamanho para que o maior lado tenha exatamente 40px
    const maxDim = Math.max(item.bounds.width, item.bounds.height)
    if (maxDim > 0) {
      item.scale(40 / maxDim)
    }

    this.history.snapshot()
    this.onChanged()
  }

  private async getOrLoadDef(sym: CatalogSymbol): Promise<paper.SymbolDefinition | null> {
    if (this.symbolDefs.has(sym.id)) return this.symbolDefs.get(sym.id)!

    try {
      const resp = await fetch(sym.file)
      const svgText = await resp.text()
      return await new Promise((resolve) => {
        paper.project.importSVG(svgText, {
          expandShapes: true,
          insert: false,
          onLoad: (imported: paper.Item) => {
            const def = new paper.SymbolDefinition(imported)
            this.symbolDefs.set(sym.id, def)
            resolve(def)
          },
          onError: () => resolve(null),
        })
      })
    } catch {
      return null
    }
  }

  setSymbol(sym: CatalogSymbol) {
    this.currentSymbol = sym
  }

  activate() {
    this.tool.activate()
    document.getElementById('croqui-canvas')!.style.cursor = 'copy'
  }

  deactivate() {
    // No specific cleanup needed, but required by ToolManager
  }
}
