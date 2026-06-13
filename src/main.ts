import { Editor } from './editor/Editor'
import { History } from './editor/History'
import { ToolManager } from './editor/ToolManager'
import { SymbolPalette } from './palette/SymbolPalette'
import paper from 'paper'
import './style.css'

const history = new History()
const editor = new Editor('croqui-canvas')

const tools = new ToolManager(history, () => updateUI())

tools.setTool('select')

const palette = new SymbolPalette('palette-container', (sym) => {
  tools.setSymbol(sym)
  if (['B3-a', 'B3-b', 'B3-c', 'B3-d', 'B6-d', 'b3-a', 'b3-b', 'b3-c', 'b3-d', 'b6-d'].includes(sym.code)) {
    document.getElementById('status-tool')!.textContent = 'Ferramenta: Desenho de Linha'
    highlightTool('pen')
  } else {
    document.getElementById('status-tool')!.textContent = 'Ferramenta: Símbolo'
    highlightTool(null)
  }
  document.getElementById('status-symbol')!.textContent = `${sym.code} — ${sym.name}`
})

palette.load()

// Take initial snapshot
history.snapshot()

// — Toolbar buttons —
function highlightTool(name: string | null) {
  document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'))
  if (name) document.getElementById(`btn-${name}`)?.classList.add('active')
}

document.getElementById('scale-select')?.addEventListener('change', () => {
  renderRuler(paper.view.zoom)
})

document.getElementById('image-opacity-slider')!.addEventListener('input', (e) => {
  const selected = tools.select.selectedItemsList
  if (selected.length === 1 && selected[0] instanceof paper.Raster) {
    const raster = selected[0] as paper.Raster
    raster.opacity = parseInt((e.target as HTMLInputElement).value) / 100
  }
})

document.getElementById('image-opacity-slider')!.addEventListener('change', () => {
  history.snapshot()
})

document.getElementById('image-bw-toggle')!.addEventListener('change', (e) => {
  const isBW = (e.target as HTMLInputElement).checked
  const selected = tools.select.selectedItemsList
  if (selected.length === 1 && selected[0] instanceof paper.Raster) {
    const raster = selected[0] as paper.Raster
    raster.data = raster.data || {}
    raster.data.isBW = isBW
    
    if (!raster.data.originalSource) {
      raster.data.originalSource = raster.source
    }
    
    if (isBW) {
      const img = raster.image
      if (img) {
        const canvas = document.createElement('canvas')
        canvas.width = img.width
        canvas.height = img.height
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.filter = 'grayscale(100%)'
          ctx.drawImage(img, 0, 0)
          raster.source = canvas.toDataURL('image/png')
        }
      }
    } else {
      raster.source = raster.data.originalSource
    }
    history.snapshot()
  }
})

document.getElementById('btn-select')!.addEventListener('click', () => {
  tools.setTool('select')
  highlightTool('select')
  palette.clearSelection()
  document.getElementById('status-tool')!.textContent = 'Ferramenta: Selecionar (Arraste para mover, [Del] para apagar, [+] e [-] para redimensionar)'
  document.getElementById('status-symbol')!.textContent = ''
})

document.getElementById('btn-pen')!.addEventListener('click', () => {
  tools.resetPen()
  tools.setTool('pen')
  highlightTool('pen')
  palette.clearSelection()
  document.getElementById('status-tool')!.textContent = 'Ferramenta: Desenho livre'
  document.getElementById('status-symbol')!.textContent = ''
})

document.getElementById('btn-text')!.addEventListener('click', () => {
  tools.setTool('text')
  highlightTool('text')
  palette.clearSelection()
  document.getElementById('status-tool')!.textContent = 'Ferramenta: Texto (Clique no canvas para escrever ou editar)'
  document.getElementById('status-symbol')!.textContent = ''
})

document.getElementById('btn-shortcut-protecao')!.addEventListener('click', () => {
  palette.setCategory('protecao')
})

document.getElementById('btn-undo')!.addEventListener('click', () => {
  history.undo()
  updateUI()
})

document.getElementById('btn-redo')!.addEventListener('click', () => {
  history.redo()
  updateUI()
})

document.getElementById('btn-bg')!.addEventListener('click', () => {
  document.getElementById('file-bg')!.click()
})

document.getElementById('file-bg')!.addEventListener('change', (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const reader = new FileReader()
    reader.onload = (evt) => {
      const dataUrl = evt.target?.result as string
      if (paper.project) {
        const raster = new paper.Raster(dataUrl)
        raster.onLoad = () => {
          raster.position = paper.view.center
          raster.opacity = 0.5
          raster.sendToBack()
          // raster.data = { locked: true } // Removed auto-lock to allow manipulation
          history.snapshot()
          
          // Switch to select tool and automatically select the image
          document.getElementById('btn-select')!.click()
          tools.select.selectItem(raster)
          updateUI()
          target.value = '' // Reset input so same file can be chosen again
        }
      }
    }
    reader.readAsDataURL(target.files[0])
  }
})

document.getElementById('btn-delete')!.addEventListener('click', () => tools.select.deleteSelected(true))
document.getElementById('btn-lock')!.addEventListener('click', () => tools.select.toggleLock())
document.getElementById('btn-rotate-left')!.addEventListener('click', () => tools.select.rotateSelected(-15))
document.getElementById('btn-rotate-right')!.addEventListener('click', () => tools.select.rotateSelected(15))
document.getElementById('btn-scale-up')!.addEventListener('click', () => tools.select.scaleSelected(1.1))
document.getElementById('btn-scale-down')!.addEventListener('click', () => tools.select.scaleSelected(0.9))

document.getElementById('btn-export-svg')!.addEventListener('click', () => editor.exportSVG())
document.getElementById('btn-export-pdf')!.addEventListener('click', () => editor.exportPDF())

// — Keyboard shortcuts —
window.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault(); history.undo(); updateUI()
  }
  if ((e.metaKey || e.ctrlKey) && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) {
    e.preventDefault(); history.redo(); updateUI()
  }
  if (e.key === 'v') { document.getElementById('btn-select')!.click() }
  if (e.key === 'p') { document.getElementById('btn-pen')!.click() }
  if (e.key === 't') { document.getElementById('btn-text')!.click() }
  if (e.key === 'l' || e.key === 'L') { document.getElementById('btn-lock')!.click() }
})

const canvas = document.getElementById('croqui-canvas') as HTMLCanvasElement

canvas.addEventListener('dragover', (e) => {
  if (e.dataTransfer?.types.includes('application/x-crocreate-symbol')) {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }
})

canvas.addEventListener('drop', async (e) => {
  e.preventDefault()
  const symId = e.dataTransfer?.getData('application/x-crocreate-symbol')
  if (symId) {
    const sym = palette.getSymbol(symId)
    if (sym && paper.view) {
      // Convert browser coordinates to Paper.js project coordinates
      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const viewPoint = new paper.Point(x, y)
      const projectPoint = paper.view.viewToProject(viewPoint)

      // Ensure SymbolTool is ready
      await tools.symbol.insertSymbolAt(sym, projectPoint)
      
      // Auto-switch to select tool so the user can immediately tweak the dropped item
      document.getElementById('btn-select')!.click()
    }
  }
})

function updateUI() {
  (document.getElementById('btn-undo') as HTMLButtonElement).disabled = !history.canUndo();
  (document.getElementById('btn-redo') as HTMLButtonElement).disabled = !history.canRedo();

  const lockBtn = document.getElementById('btn-lock')!
  if (tools.select.selectionCount > 0) {
    lockBtn.title = 'Travar Seleção (L)'
    lockBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
    lockBtn.style.color = '' // default
  } else {
    lockBtn.title = 'Destravar Tudo (L)'
    // Unlock icon
    lockBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>'
    lockBtn.style.color = '#eab308' // yellowish to indicate unlock mode
  }

  const imgProps = document.getElementById('image-properties')!
  const bwToggle = document.getElementById('image-bw-toggle') as HTMLInputElement
  const opacitySlider = document.getElementById('image-opacity-slider') as HTMLInputElement

  const selected = tools.select.selectedItemsList
  if (selected.length === 1 && selected[0] instanceof paper.Raster) {
    imgProps.style.display = 'flex'
    const raster = selected[0] as paper.Raster
    if (document.activeElement !== opacitySlider) {
      opacitySlider.value = Math.round(raster.opacity * 100).toString()
    }
    bwToggle.checked = !!raster.data?.isBW
  } else {
    imgProps.style.display = 'none'
  }
}

setInterval(updateUI, 100)

tools.onToolChange = (name) => {
  if (name !== 'symbol') {
    document.getElementById('status-symbol')!.textContent = ''
  }
}

// — View & Altitude Ruler —
editor.onViewChange = (zoom) => {
  const wrap = document.getElementById('canvas-wrap')!
  
  const scaledGrid = 50 * zoom
  wrap.style.backgroundSize = `${scaledGrid}px ${scaledGrid}px`
  
  const offsetX = -paper.view.bounds.x * zoom
  const offsetY = -paper.view.bounds.y * zoom
  wrap.style.backgroundPosition = `${offsetX}px ${offsetY}px`
  renderRuler(zoom)
}

document.getElementById('toggle-ruler')?.addEventListener('change', (e) => {
  const isChecked = (e.target as HTMLInputElement).checked
  document.getElementById('altitude-ruler')!.style.display = isChecked ? 'block' : 'none'
  const wrap = document.getElementById('canvas-wrap')!
  if (!isChecked) {
    wrap.style.backgroundImage = 'none'
  } else {
    wrap.style.backgroundImage = '' // returns to css default
  }
})

function renderRuler(zoom = 1) {
  const ruler = document.getElementById('altitude-ruler')!
  ruler.innerHTML = ''
  
  if (!paper.project) return
  
  const startY = paper.view.bounds.y
  const endY = paper.view.bounds.y + paper.view.bounds.height
  
  // Find the first multiple of 50 that is >= startY
  const firstTick = Math.ceil(startY / 50) * 50
  
  // Pegamos a escala selecionada pelo usuário
  const scaleSelect = document.getElementById('scale-select') as HTMLSelectElement
  const metersPerGrid = scaleSelect ? parseInt(scaleSelect.value) : 10
  
  for (let y = firstTick; y <= endY; y += 50) {
    const screenY = (y - startY) * zoom
    // Y=0 é o chão. 50px de altura no canvas representam "metersPerGrid" metros.
    const altitude = Math.round(-y * (metersPerGrid / 50))
    
    // Limita entre o nível do chão (0m) e o Everest (~8850m)
    if (altitude < 0 || altitude > 8850) continue
    
    const tick = document.createElement('div')
    tick.className = 'ruler-tick'
    tick.style.top = `${screenY}px`
    tick.textContent = `${altitude}m`
    ruler.appendChild(tick)
  }
}

// Initial draw
setTimeout(() => {
  if (paper.project) {
    // Alinha a visualização inicial para que o chão (Y=0) fique próximo da borda inferior
    paper.view.center = new paper.Point(
      paper.view.center.x, 
      -paper.view.bounds.height / 2 + 50
    )
  }
  
  if (editor.onViewChange) {
    editor.onViewChange(paper.view.zoom, paper.view.center.x, paper.view.center.y)
  }
}, 50)

// Listen to scale change
const scaleSelect = document.getElementById('scale-select') as HTMLSelectElement
let currentMetersPerGrid = scaleSelect ? parseInt(scaleSelect.value) : 5
if (scaleSelect) {
  scaleSelect.addEventListener('change', () => {
    const newMeters = parseInt(scaleSelect.value)
    const factor = currentMetersPerGrid / newMeters
    
    // Scale all drawn items relative to ground (Y=0) and horizontal origin (X=0)
    if (paper.project && paper.project.activeLayer) {
      paper.project.activeLayer.children.forEach(item => {
        item.scale(factor, new paper.Point(0, 0))
      })
      // Save state to history since we modified the drawing
      history.snapshot()
    }
    
    currentMetersPerGrid = newMeters
    
    if (editor.onViewChange) {
      editor.onViewChange(paper.view.zoom, paper.view.center.x, paper.view.center.y)
    }
  })
}
