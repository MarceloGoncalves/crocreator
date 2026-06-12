import paper from 'paper'

const MAX_HISTORY = 50

export class History {
  private stack: string[] = []
  private cursor = -1

  snapshot() {
    const json = paper.project.exportJSON()
    // Discard any redo states ahead of cursor
    this.stack = this.stack.slice(0, this.cursor + 1)
    this.stack.push(json)
    if (this.stack.length > MAX_HISTORY) this.stack.shift()
    this.cursor = this.stack.length - 1
  }

  undo(): boolean {
    if (this.cursor <= 0) return false
    this.cursor--
    paper.project.clear()
    paper.project.importJSON(this.stack[this.cursor])
    return true
  }

  redo(): boolean {
    if (this.cursor >= this.stack.length - 1) return false
    this.cursor++
    paper.project.clear()
    paper.project.importJSON(this.stack[this.cursor])
    return true
  }

  canUndo() { return this.cursor > 0 }
  canRedo() { return this.cursor < this.stack.length - 1 }
}
