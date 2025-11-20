/**
 * Noise generation utilities
 * Implements various noise algorithms for Canvas rendering
 */

/**
 * Simple 2D Perlin-like noise implementation
 */
export class NoiseGenerator {
  private permutation: number[]

  constructor(seed: number = Date.now()) {
    this.permutation = this.generatePermutation(seed)
  }

  private generatePermutation(seed: number): number[] {
    const p = []
    for (let i = 0; i < 256; i++) {
      p[i] = i
    }

    // Fisher-Yates shuffle with seed
    let random = seed
    for (let i = 255; i > 0; i--) {
      random = (random * 9301 + 49297) % 233280
      const j = Math.floor((random / 233280) * (i + 1))
      ;[p[i], p[j]] = [p[j], p[i]]
    }

    return [...p, ...p] // Duplicate for wrapping
  }

  private fade(t: number): number {
    return t * t * t * (t * (t * 6 - 15) + 10)
  }

  private lerp(t: number, a: number, b: number): number {
    return a + t * (b - a)
  }

  private grad(hash: number, x: number, y: number): number {
    const h = hash & 7
    const u = h < 4 ? x : y
    const v = h < 4 ? y : x
    return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v)
  }

  /**
   * Generate 2D Perlin noise value at (x, y)
   * Returns value between -1 and 1
   */
  perlin2D(x: number, y: number): number {
    const X = Math.floor(x) & 255
    const Y = Math.floor(y) & 255

    x -= Math.floor(x)
    y -= Math.floor(y)

    const u = this.fade(x)
    const v = this.fade(y)

    const a = this.permutation[X] + Y
    const aa = this.permutation[a]
    const ab = this.permutation[a + 1]
    const b = this.permutation[X + 1] + Y
    const ba = this.permutation[b]
    const bb = this.permutation[b + 1]

    return this.lerp(
      v,
      this.lerp(u, this.grad(this.permutation[aa], x, y), this.grad(this.permutation[ba], x - 1, y)),
      this.lerp(
        u,
        this.grad(this.permutation[ab], x, y - 1),
        this.grad(this.permutation[bb], x - 1, y - 1),
      ),
    )
  }

  /**
   * Generate Fractional Brownian Motion (multi-octave noise)
   */
  fbm(x: number, y: number, octaves: number = 4, persistence: number = 0.5): number {
    let total = 0
    let frequency = 1
    let amplitude = 1
    let maxValue = 0

    for (let i = 0; i < octaves; i++) {
      total += this.perlin2D(x * frequency, y * frequency) * amplitude
      maxValue += amplitude
      amplitude *= persistence
      frequency *= 2
    }

    return total / maxValue
  }

  /**
   * Generate turbulence (absolute value of noise)
   */
  turbulence(x: number, y: number, size: number): number {
    let value = 0
    let initialSize = size

    while (size >= 1) {
      value += Math.abs(this.perlin2D(x / size, y / size)) * size
      size /= 2
    }

    return value / initialSize
  }

  /**
   * Generate marble-like pattern
   */
  marble(x: number, y: number, scale: number = 10, turbulencePower: number = 5): number {
    const xyValue = x * scale + y * scale
    const sineValue = Math.abs(Math.sin(xyValue + turbulencePower * this.turbulence(x, y, 32)))
    return sineValue
  }

  /**
   * Generate Worley/Voronoi noise
   */
  worley(x: number, y: number, scale: number = 10): number {
    const cellX = Math.floor(x * scale)
    const cellY = Math.floor(y * scale)

    let minDist = Infinity

    // Check neighboring cells
    for (let i = -1; i <= 1; i++) {
      for (let j = -1; j <= 1; j++) {
        const neighborX = cellX + i
        const neighborY = cellY + j

        // Generate pseudo-random point in cell
        const hash = this.permutation[(this.permutation[neighborX & 255] + neighborY) & 255]
        const pointX = neighborX + (hash / 255)
        const pointY = neighborY + ((this.permutation[hash] / 255))

        // Calculate distance
        const dx = x * scale - pointX
        const dy = y * scale - pointY
        const dist = Math.sqrt(dx * dx + dy * dy)

        minDist = Math.min(minDist, dist)
      }
    }

    return 1 - Math.min(minDist, 1)
  }
}

/**
 * Color utilities
 */
export function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  const c = (1 - Math.abs(2 * l - 1)) * s
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1))
  const m = l - c / 2

  let r = 0,
    g = 0,
    b = 0

  if (h < 60) {
    r = c
    g = x
    b = 0
  } else if (h < 120) {
    r = x
    g = c
    b = 0
  } else if (h < 180) {
    r = 0
    g = c
    b = x
  } else if (h < 240) {
    r = 0
    g = x
    b = c
  } else if (h < 300) {
    r = x
    g = 0
    b = c
  } else {
    r = c
    g = 0
    b = x
  }

  return [Math.round((r + m) * 255), Math.round((g + m) * 255), Math.round((b + m) * 255)]
}

/**
 * Render noise to canvas
 */
export function renderNoiseToCanvas(
  canvas: HTMLCanvasElement,
  type: string,
  parameters: Record<string, any>,
) {
  const ctx = canvas.getContext("2d")
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height
  const imageData = ctx.createImageData(width, height)
  const data = imageData.data

  const noise = new NoiseGenerator(parameters.seed || Date.now())
  const scale = parameters.scale || 0.01
  const octaves = parameters.octaves || 4
  const persistence = parameters.persistence || 0.5

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const i = (y * width + x) * 4

      let value = 0

      switch (type) {
        case "perlin":
          value = noise.perlin2D(x * scale, y * scale)
          break
        case "fbm":
          value = noise.fbm(x * scale, y * scale, octaves, persistence)
          break
        case "turbulence":
          value = noise.turbulence(x, y, 64)
          break
        case "marble":
          value = noise.marble(x, y, scale * 100, parameters.turbulencePower || 5)
          break
        case "worley":
          value = noise.worley(x / width, y / height, parameters.cellCount || 10)
          break
        default:
          value = noise.perlin2D(x * scale, y * scale)
      }

      // Normalize to 0-1
      value = (value + 1) / 2

      // Apply color mapping
      const colorMode = parameters.colorMode || "grayscale"

      if (colorMode === "grayscale") {
        const gray = Math.floor(value * 255)
        data[i] = gray
        data[i + 1] = gray
        data[i + 2] = gray
      } else if (colorMode === "hue") {
        const hue = value * 360
        const [r, g, b] = hslToRgb(hue, 0.7, 0.5)
        data[i] = r
        data[i + 1] = g
        data[i + 2] = b
      } else if (colorMode === "gradient") {
        // Two-color gradient
        const color1 = parameters.color1 || [0, 0, 255]
        const color2 = parameters.color2 || [255, 0, 0]
        data[i] = Math.floor(color1[0] + (color2[0] - color1[0]) * value)
        data[i + 1] = Math.floor(color1[1] + (color2[1] - color1[1]) * value)
        data[i + 2] = Math.floor(color1[2] + (color2[2] - color1[2]) * value)
      }

      data[i + 3] = 255 // Alpha
    }
  }

  ctx.putImageData(imageData, 0, 0)
}
