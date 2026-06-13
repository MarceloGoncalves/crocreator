import paper from 'paper'
import type { History } from '../History'

function openDeleteModal(count: number): Promise<boolean> {
  return new Promise((resolve) => {
    const overlay = document.getElementById('delete-modal-overlay')!
    const textEl = document.getElementById('delete-modal-text')!
    const btnCancel = document.getElementById('delete-modal-cancel')!
    const btnConfirm = document.getElementById('delete-modal-confirm')!

    textEl.textContent = `Tem certeza que deseja excluir ${count} item(s)? Essa ação não pode ser desfeita (mas você pode usar Ctrl+Z).`
    overlay.classList.remove('hidden')

    const cleanup = () => {
      overlay.classList.add('hidden')
      btnCancel.removeEventListener('click', onCancel)
      btnConfirm.removeEventListener('click', onConfirm)
      document.removeEventListener('keydown', onKey)
    }

    const onCancel = () => { cleanup(); resolve(false) }
    const onConfirm = () => { cleanup(); resolve(true) }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter') onConfirm()
      if (e.key === 'Escape') onCancel()
    }

    btnCancel.addEventListener('click', onCancel)
    btnConfirm.addEventListener('click', onConfirm)
    document.addEventListener('keydown', onKey)
  })
}

export class SelectTool {
  private tool: paper.Tool
  private selectedItems = new Set<paper.Item>()
  private dragStart: paper.Point | null = null
  private wasDragged = false
  private selectionRect: paper.Path.Rectangle | null = null
  private selectionStart: paper.Point | null = null
  private history: History
  private onChanged: () => void

  constructor(history: History, onChanged: () => void) {
    this.history = history
    this.onChanged = onChanged
    this.tool = new paper.Tool()

    this.tool.onMouseDown = (event: paper.ToolEvent) => {
      this.wasDragged = false
      const hit = paper.project.hitTest(event.point, {
        fill: true, stroke: true, segments: true, tolerance: 8,
        match: (res: paper.HitResult) => {
          let i: paper.Item | null = res.item
          while (i) {
            if (i.data?.locked) return false
            i = i.parent
          }
          return true
        }
      })

      if (hit?.item) {
        let item: paper.Item = hit.item
        while (item.parent && !(item.parent instanceof paper.Layer)) {
          item = item.parent
        }
        
        if (!event.modifiers.shift && !this.selectedItems.has(item)) {
          this.clearSelection()
        }
        
        if (event.modifiers.shift && this.selectedItems.has(item)) {
          item.selected = false
          this.selectedItems.delete(item)
        } else {
          item.selected = true
          this.selectedItems.add(item)
        }
        this.dragStart = event.point
      } else {
        if (!event.modifiers.shift) {
          this.clearSelection()
        }
        this.selectionStart = event.point
      }
    }

    this.tool.onMouseDrag = (event: paper.ToolEvent) => {
      if (this.selectedItems.size > 0 && this.dragStart) {
        this.selectedItems.forEach(item => {
          item.position = item.position.add(event.delta)
        })
        this.wasDragged = true
      } else if (this.selectionStart) {
        if (this.selectionRect) {
          this.selectionRect.remove()
        }
        const rect = new paper.Rectangle(this.selectionStart, event.point)
        this.selectionRect = new paper.Path.Rectangle(rect)
        this.selectionRect.strokeColor = new paper.Color('#3b82f6')
        this.selectionRect.fillColor = new paper.Color(0.23, 0.51, 0.96, 0.2) // semi-transparent blue
      }
    }

    this.tool.onMouseUp = () => {
      if (this.selectionRect) {
        const bounds = this.selectionRect.bounds
        paper.project.activeLayer.children.forEach(item => {
          if (item !== this.selectionRect && !item.data?.locked && item.bounds.intersects(bounds)) {
            item.selected = true
            this.selectedItems.add(item)
          }
        })
        this.selectionRect.remove()
        this.selectionRect = null
        this.selectionStart = null
      } else if (this.selectedItems.size > 0 && this.wasDragged) {
        this.history.snapshot()
        this.onChanged()
        this.wasDragged = false
      }
    }

    this.tool.onKeyDown = (event: paper.KeyEvent) => {
      if (this.selectedItems.size === 0) return
      
      if (event.key === 'delete' || event.key === 'backspace') {
        this.deleteSelected()
      } else if (event.key === '+' || event.key === '=') {
        this.scaleSelected(1.1)
      } else if (event.key === '-') {
        this.scaleSelected(0.9)
      } else if (event.key === '[') {
        this.rotateSelected(-15)
      } else if (event.key === ']') {
        this.rotateSelected(15)
      } else if (event.key === 'up') {
        this.nudgeSelected(0, event.modifiers.shift ? -10 : -1)
        event.preventDefault()
      } else if (event.key === 'down') {
        this.nudgeSelected(0, event.modifiers.shift ? 10 : 1)
        event.preventDefault()
      } else if (event.key === 'left') {
        this.nudgeSelected(event.modifiers.shift ? -10 : -1, 0)
        event.preventDefault()
      } else if (event.key === 'right') {
        this.nudgeSelected(event.modifiers.shift ? 10 : 1, 0)
        event.preventDefault()
      }
    }
  }

  nudgeSelected(dx: number, dy: number) {
    if (this.selectedItems.size === 0) return
    this.selectedItems.forEach(item => {
      item.position = item.position.add(new paper.Point(dx, dy))
    })
    this.history.snapshot()
    this.onChanged()
  }

  selectItem(item: paper.Item) {
    if (item.data?.locked) return
    this.clearSelection()
    item.selected = true
    this.selectedItems.add(item)
    this.onChanged()
  }

  async deleteSelected(promptUser: boolean = false) {
    if (this.selectedItems.size === 0) return
    if (promptUser) {
      const confirmed = await openDeleteModal(this.selectedItems.size)
      if (!confirmed) return
    }
    this.selectedItems.forEach(item => item.remove())
    this.selectedItems.clear()
    this.history.snapshot()
    this.onChanged()
  }

  scaleSelected(factor: number) {
    if (this.selectedItems.size === 0) return
    this.selectedItems.forEach(item => item.scale(factor))
    this.history.snapshot()
    this.onChanged()
  }

  rotateSelected(angle: number) {
    if (this.selectedItems.size === 0) return
    this.selectedItems.forEach(item => item.rotate(angle))
    this.history.snapshot()
    this.onChanged()
  }

  get selectionCount() {
    return this.selectedItems.size
  }

  clearSelection() {
    this.selectedItems.forEach(item => item.selected = false)
    this.selectedItems.clear()
  }

  toggleLock() {
    if (this.selectedItems.size > 0) {
      // Lock selected items
      this.selectedItems.forEach(item => {
        item.data = item.data || {}
        item.data.locked = true
        item.selected = false // visually deselect it
      })
      this.selectedItems.clear()
      this.history.snapshot()
      this.onChanged()
    } else {
      // Unlock all items
      let unlockedSomething = false
      if (paper.project && paper.project.activeLayer) {
        paper.project.activeLayer.children.forEach(item => {
          if (item.data?.locked) {
            item.data.locked = false
            item.selected = true
            this.selectedItems.add(item)
            unlockedSomething = true
          }
        })
      }
      if (unlockedSomething) {
        this.history.snapshot()
        this.onChanged()
      }
    }
  }

  activate() {
    this.tool.activate()
    document.getElementById('croqui-canvas')!.style.cursor = 'default'
  }

  deactivate() {
    this.clearSelection()
  }
}
