import paper from 'paper'
import type { History } from '../History'

export class PenTool {
  private tool: paper.Tool
  private currentPath: paper.Path | null = null
  private onChanged: () => void

  strokeColor = '#e2e8f0'
  strokeWidth = 3
  dashArray: number[] | null = null
  decorationType: 'none' | 'arrows' | 'laca' = 'none'

  constructor(history: History, onChanged: () => void) {
    this.onChanged = onChanged
    this.tool = new paper.Tool()
    this.tool.minDistance = 4

    this.tool.onMouseDown = (event: paper.ToolEvent) => {
      this.currentPath = new paper.Path({
        strokeColor: this.strokeColor,
        strokeWidth: this.strokeWidth,
        strokeCap: 'round',
        strokeJoin: 'round',
        dashArray: this.dashArray || [],
      })
      this.currentPath.add(event.point)
    }

    this.tool.onMouseDrag = (event: paper.ToolEvent) => {
      this.currentPath?.add(event.point)
    }

    this.tool.onMouseUp = () => {
      if (this.currentPath) {
        this.currentPath.simplify(6)
        
        if (this.decorationType !== 'none' && this.currentPath.length > 20) {
          const group = new paper.Group([this.currentPath])
          
          if (this.decorationType === 'arrows') {
            const arrowSpacing = 40 // pixels between arrows
            for (let offset = arrowSpacing / 2; offset < this.currentPath.length; offset += arrowSpacing) {
              const point = this.currentPath.getPointAt(offset)
              const tangent = this.currentPath.getTangentAt(offset)
              
              const arrow = new paper.Path({
                segments: [
                  new paper.Point(-6, -4),
                  new paper.Point(4, 0),
                  new paper.Point(-6, 4)
                ],
                fillColor: this.strokeColor,
                closed: true
              })
              arrow.scale(this.strokeWidth / 2)
              arrow.position = point
              arrow.rotation = tangent.angle
              group.addChild(arrow)
            }
          } else if (this.decorationType === 'laca') {
            const segmentSpacing = 15 // closer spacing for laca
            const scale = this.strokeWidth / 2
            for (let offset = segmentSpacing / 2; offset < this.currentPath.length; offset += segmentSpacing) {
              const point = this.currentPath.getPointAt(offset)
              const tangent = this.currentPath.getTangentAt(offset)
              const normal = new paper.Point(-tangent.y, tangent.x) // perpendicular direction
              
              const lacaLine = new paper.Path({
                segments: [
                  point,
                  point.add(normal.multiply(8 * scale)) // scaled perpendicular line
                ],
                strokeColor: this.strokeColor,
                strokeWidth: this.strokeWidth,
                strokeCap: 'round'
              })
              group.addChild(lacaLine)
            }
          }
        }
        
        this.currentPath = null
        history.snapshot()
        this.onChanged()
      }
    }
  }

  activate() {
    this.tool.activate()
    document.getElementById('croqui-canvas')!.style.cursor = 'crosshair'
  }

  deactivate() {}
}
