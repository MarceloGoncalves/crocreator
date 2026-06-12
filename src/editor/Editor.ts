import paper from 'paper'
import { jsPDF } from 'jspdf'

export class Editor {
  private canvas: HTMLCanvasElement

  constructor(canvasId: string) {
    this.canvas = document.getElementById(canvasId) as HTMLCanvasElement
    paper.setup(this.canvas)

    // Removemos o fundo branco para ver a malha do CSS

    // Handle resize
    window.addEventListener('resize', () => {
      paper.view.viewSize = new paper.Size(
        this.canvas.offsetWidth,
        this.canvas.offsetHeight,
      )
      this.fireViewChange()
    })

    // Zoom and Pan
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault()
      if (e.ctrlKey || e.metaKey) {
        // Zoom
        const oldZoom = paper.view.zoom
        const factor = e.deltaY < 0 ? 1.05 : 0.95
        let newZoom = oldZoom * factor
        newZoom = Math.max(0.2, Math.min(newZoom, 5)) // Clamp zoom
        
        const mousePosition = new paper.Point(e.offsetX, e.offsetY)
        const viewPosition = paper.view.viewToProject(mousePosition)
        
        paper.view.zoom = newZoom
        const newViewPosition = paper.view.viewToProject(mousePosition)
        const centerDelta = newViewPosition.subtract(viewPosition)
        paper.view.center = paper.view.center.subtract(centerDelta)
      } else {
        // Pan
        const delta = new paper.Point(e.deltaX, e.deltaY).divide(paper.view.zoom)
        paper.view.center = paper.view.center.add(delta)
      }
      
      // Bloqueia o scroll/zoom para não ultrapassar a marca do chão (Y=0)
      // Mantemos uma margem de 50px do limite inferior da tela
      const maxBottom = 50
      const currentBottom = paper.view.center.y + paper.view.bounds.height / 2
      if (currentBottom > maxBottom) {
        paper.view.center = new paper.Point(
          paper.view.center.x,
          maxBottom - paper.view.bounds.height / 2
        )
      }
      
      this.fireViewChange()
    })
  }

  onViewChange?: (zoom: number, centerX: number, centerY: number) => void

  private fireViewChange() {
    this.onViewChange?.(paper.view.zoom, paper.view.center.x, paper.view.center.y)
  }

  private createExportGrid(): paper.Group {
    const group = new paper.Group()
    const bounds = paper.view.bounds

    const scaleSelect = document.getElementById('scale-select') as HTMLSelectElement
    const metersPerGrid = scaleSelect ? parseInt(scaleSelect.value) : 10

    const firstY = Math.floor(bounds.top / 50) * 50

    // Draw horizontal grid lines and altitude text
    for (let y = firstY; y <= bounds.bottom; y += 50) {
      const line = new paper.Path.Line(new paper.Point(bounds.left, y), new paper.Point(bounds.right, y))
      line.strokeColor = new paper.Color(0, 0, 0, 0.02) // Opacidade bem menor
      line.dashArray = [4, 8] // Linha tracejada para ficar ainda mais leve
      group.addChild(line)

      const altitude = Math.round(-y * (metersPerGrid / 50))
      if (altitude >= 0 && altitude <= 8850) {
        const text = new paper.PointText(new paper.Point(bounds.left + 15 / paper.view.zoom, y - 5 / paper.view.zoom))
        text.content = `${altitude}m`
        text.fillColor = new paper.Color('#1e293b')
        text.fontSize = 14 / paper.view.zoom
        text.fontWeight = 'bold'
        
        const bg = new paper.Path.Rectangle(text.bounds.expand(4 / paper.view.zoom))
        bg.fillColor = new paper.Color(1, 1, 1, 0.8)
        
        const labelGroup = new paper.Group([bg, text])
        group.addChild(labelGroup)
      }
    }

    group.sendToBack()
    return group
  }

  exportSVG(filename = 'croqui.svg') {
    const grid = this.createExportGrid()
    paper.view.update()
    const svg = paper.project.exportSVG({ asString: true }) as string
    grid.remove()
    
    const blob = new Blob([svg], { type: 'image/svg+xml' })
    this.download(blob, filename)
  }

  exportPDF(filename = 'croqui.pdf') {
    const grid = this.createExportGrid()
    paper.view.update()
    const svg = paper.project.exportSVG({ asString: true }) as string
    grid.remove()

    const w = paper.view.viewSize.width
    const h = paper.view.viewSize.height
    const pdf = new jsPDF({
      orientation: w > h ? 'landscape' : 'portrait',
      unit: 'px',
      format: [w, h],
    })
    pdf.addSvgAsImage(svg, 0, 0, w, h)
    pdf.save(filename)
  }

  private download(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }
}
