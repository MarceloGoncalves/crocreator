import type { ToolName } from '../types'
import type { History } from './History'
import { SelectTool } from './tools/SelectTool'
import { PenTool } from './tools/PenTool'
import { SymbolTool } from './tools/SymbolTool'
import { TextTool } from './tools/TextTool'
import type { CatalogSymbol } from '../types'

export class ToolManager {
  select: SelectTool
  pen: PenTool
  symbol: SymbolTool
  text: TextTool
  private active: ToolName = 'select'
  onToolChange?: (tool: ToolName) => void

  constructor(history: History, onChanged: () => void) {
    this.select = new SelectTool(history, onChanged)
    this.pen = new PenTool(history, onChanged)
    this.symbol = new SymbolTool(history, onChanged)
    this.text = new TextTool(history, onChanged)
  }

  setTool(name: ToolName) {
    if (this.active === 'select') this.select.deactivate()
    else if (this.active === 'pen') this.pen.deactivate()
    else if (this.active === 'symbol') this.symbol.deactivate()
    else if (this.active === 'text') this.text.deactivate()

    this.active = name
    
    if (name === 'select') this.select.activate()
    else if (name === 'pen') this.pen.activate()
    else if (name === 'symbol') this.symbol.activate()
    else if (name === 'text') this.text.activate()
    
    this.onToolChange?.(name)
  }

  setSymbol(sym: CatalogSymbol) {
    // Variante (B3-a), Artificial (B3-b), Caminhada (B3-c), Corda fixa (B3-d) e Fissura em Laca (B6-d)
    // funcionam como ferramentas de caneta.
    if (['B3-a', 'B3-b', 'B3-c', 'B3-d', 'B6-d', 'b3-a', 'b3-b', 'b3-c', 'b3-d', 'b6-d'].includes(sym.code)) {
      this.pen.strokeColor = sym.color || '#000000'
      this.pen.strokeWidth = 3
      this.pen.decorationType = 'none' // default
      
      if (sym.code.toLowerCase() === 'b3-a') {
        // Rota da via ou variante -> tracejada
        this.pen.dashArray = [8, 8]
      } else if (sym.code.toLowerCase() === 'b3-b') {
        // Rota em Artificial -> pontilhada
        this.pen.dashArray = [2, 8]
        this.pen.strokeWidth = 4
      } else if (sym.code.toLowerCase() === 'b3-c') {
        // Trecho de caminhada -> linha com pequenas flechas apontando a direção
        this.pen.dashArray = null
        this.pen.strokeWidth = 2
        this.pen.decorationType = 'arrows'
      } else if (sym.code.toLowerCase() === 'b3-d') {
        // Corda fixa ou cabo de aço -> contínuo com pontinho (dash-dot)
        this.pen.dashArray = [12, 6, 2, 6]
      } else if (sym.code.toLowerCase() === 'b6-d') {
        // Fissura em Laca -> linha contínua com segmentos perpendiculares (laca)
        this.pen.dashArray = null
        this.pen.strokeWidth = 2
        this.pen.decorationType = 'laca'
      }
      
      this.setTool('pen')
    } else {
      this.symbol.setSymbol(sym)
      this.setTool('symbol')
    }
  }

  resetPen() {
    this.pen.strokeColor = '#e2e8f0'
    this.pen.strokeWidth = 3
    this.pen.dashArray = null
    this.pen.decorationType = 'none'
  }

  get activeTool() { return this.active }
}
