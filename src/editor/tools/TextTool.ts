import paper from 'paper'
import type { History } from '../History'

function openTextModal(initialText: string = ''): Promise<string | null> {
  return new Promise((resolve) => {
    const overlay = document.getElementById('text-modal-overlay')!
    const input = document.getElementById('text-modal-input') as HTMLInputElement
    const btnCancel = document.getElementById('text-modal-cancel')!
    const btnConfirm = document.getElementById('text-modal-confirm')!

    input.value = initialText
    overlay.classList.remove('hidden')
    
    // Pequeno timeout para o navegador renderizar antes de focar
    setTimeout(() => {
      input.focus()
      input.select()
    }, 50)

    const cleanup = () => {
      overlay.classList.add('hidden')
      btnCancel.removeEventListener('click', onCancel)
      btnConfirm.removeEventListener('click', onConfirm)
      input.removeEventListener('keydown', onKey)
    }

    const onCancel = () => { cleanup(); resolve(null) }
    const onConfirm = () => { cleanup(); resolve(input.value) }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter') onConfirm()
      if (e.key === 'Escape') onCancel()
    }

    btnCancel.addEventListener('click', onCancel)
    btnConfirm.addEventListener('click', onConfirm)
    input.addEventListener('keydown', onKey)
  })
}

export class TextTool {
  private tool: paper.Tool
  private history: History
  private onChanged: () => void

  constructor(history: History, onChanged: () => void) {
    this.history = history
    this.onChanged = onChanged
    this.tool = new paper.Tool()

    this.tool.onMouseDown = async (event: paper.ToolEvent) => {
      // Check if we clicked on an existing text to edit it
      const hit = paper.project.hitTest(event.point, {
        fill: true, stroke: true, tolerance: 8,
      })

      if (hit?.item instanceof paper.PointText) {
        const text = await openTextModal(hit.item.content)
        if (text !== null) {
          if (text.trim() === '') {
            hit.item.remove()
          } else {
            hit.item.content = text
          }
          this.history.snapshot()
          this.onChanged()
        }
        return
      }

      // Otherwise, create new text
      const text = await openTextModal('')
      if (text && text.trim() !== '') {
        new paper.PointText({
          point: event.point,
          content: text,
          fillColor: '#1a1a1a', // dark text
          fontFamily: 'Andika, sans-serif',
          fontWeight: '700', // Andika bold is 700
          fontSize: 20, // increased visibility
          shadowColor: '#ffffff', // white glow to ensure readability on dark backgrounds
          shadowBlur: 8,
          shadowOffset: new paper.Point(1, 1)
        })
        this.history.snapshot()
        this.onChanged()
      }
    }
  }

  activate() {
    this.tool.activate()
    document.getElementById('croqui-canvas')!.style.cursor = 'text'
  }

  deactivate() {}
}
