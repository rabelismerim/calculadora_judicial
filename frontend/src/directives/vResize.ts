function debounce(func: Function, delay: number) {
  let timer: any
  return function (...args: any) {
    clearTimeout(timer)
    timer = setTimeout(() => func(...args), delay)
  }
}

interface IResizeData {
  width: number
  height: number
}

export interface IOptions {
  /**
   * @default 50
   */
  delay?: number
  wait?: number
  resize?: (data: IResizeData, target: Element) => any
}

class Resizer {
  private resizeObserver: ResizeObserver | null = null
  private element: HTMLElement | null
  private width = 0
  private height = 0
  private options: IOptions

  constructor(el: string | HTMLElement, options?: IOptions) {
    let $el = el
    if (typeof el === 'string')
      $el = document.querySelector(el) as HTMLElement

    this.element = $el as HTMLElement
    this.options = Object.assign({
      delay: 150,
    }, options)

    this.observe(this.element)
  }

  public observe(element?: HTMLElement): void {
    if (element)
      this.element = element

    else
      element = this.element as HTMLElement

    if (!(element instanceof HTMLElement))
      throw new Error('The target element must be a HTMLElement')

    const { width, height } = element.getBoundingClientRect()
    this.width = Math.floor(width)
    this.height = Math.floor(height)

    if (this.resizeObserver)
      this.disconnect()

    this.resizeObserver = new ResizeObserver(this._onResize())
    this.resizeObserver.observe(element)
  }

  private _onResize() {
    const delay = this.options.delay || this.options.wait
    if (delay)
      return debounce(this._handleResize.bind(this), delay)

    return this._handleResize.bind(this)
  }

  private _handleResize(entries: ResizeObserverEntry[]) {
    for (const entry of entries) {
      const target = entry.target
      let { width, height } = target.getBoundingClientRect()
      width = Math.floor(width)
      height = Math.floor(height)

      if (this.width !== width || this.height !== height) {
        this.width = width
        this.height = height

        if (typeof this.options.resize === 'function')
          this.options.resize({ width, height }, target)
      }
    }
  }

  public disconnect() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
      this.resizeObserver = null
    }
  }

  public destroy() {
    this.disconnect()
    this.element = null
  }
}

function getOptions({ value, arg }: any): IOptions {
  const options: IOptions = {}
  if (typeof value === 'function')
    options.resize = value

  options.delay = isNaN(parseInt(arg)) ? 50 : parseInt(arg)

  return options
}

const directive = {
  mounted(el: any, binding: any) {
    const { value } = binding
    if (value && typeof value !== 'function')
      return console.warn('v-resize should received a function as value')

    if (!(el.getBoundingClientRect))
      throw new Error('The target element must be a HTMLElement')

    const { width, height } = el.getBoundingClientRect()
    binding.value({
      width: Math.floor(width),
      height: Math.floor(height),
    }, el)

    const ro = new Resizer(el, getOptions(binding))
    el.__vue_resize__ = ro
  },
  beforeUnmount(el: any) {
    const ro = el.__vue_resize__
    if (ro)
      ro.destroy()
  },
}

export default directive
