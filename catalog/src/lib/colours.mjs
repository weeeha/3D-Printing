/**
 * Filament colour and finish mapping.
 *
 * Hex values are a best reading of Bambu Lab's published colour codes and of
 * third-party product photos. They are NOT sampled from physical spools and
 * are expected to need correction once compared against the real shelf.
 * This file has exactly one responsibility so that correcting them is cheap.
 *
 * Key formats, all lowercase:
 *   "11101"                        Bambu five-digit colour code
 *   "pine green"                   Bambu colour name where no code was in the email
 *   "creality:hyper pla:grey"      third party, brand:productLine:colourName
 *
 * @typedef {"basic"|"matte"|"silk"|"sparkle"|"translucent"|"dual"|"rainbow"|"glow"|"marble"} Finish
 * @typedef {{ hex: string, finish: Finish, hex2?: string }} Swatch
 */

/** @type {Record<string, Swatch>} */
export const COLOURS = {
  // --- Bambu PLA Basic ---
  "10201": { hex: "#F7E6DE", finish: "basic" },
  "10202": { hex: "#EC008C", finish: "basic" },
  "10300": { hex: "#FF6A13", finish: "basic" },
  "10400": { hex: "#F4EE2A", finish: "basic" },
  "10502": { hex: "#3F8E43", finish: "basic" },
  "10602": { hex: "#5B6579", finish: "basic" },
  "10700": { hex: "#5E43B7", finish: "basic" },
  "red": { hex: "#C00D1E", finish: "basic" },

  // --- Bambu PLA Matte ---
  "11100": { hex: "#FFFFFF", finish: "matte" },
  "11101": { hex: "#1A1A1A", finish: "matte" },
  "11200": { hex: "#DE4343", finish: "matte" },
  "11201": { hex: "#E8AFCF", finish: "matte" },
  "11400": { hex: "#F7D959", finish: "matte" },
  "11600": { hex: "#0078BF", finish: "matte" },
  "11601": { hex: "#A3D8E1", finish: "matte" },
  "matte charcoal": { hex: "#1A1A1A", finish: "matte" },

  // --- Bambu PLA Silk ---
  "13104": { hex: "#A6A9AA", finish: "silk" },
  "13401": { hex: "#F4A925", finish: "silk" },
  "13701": { hex: "#8E4EC6", finish: "silk" },
  "gold": { hex: "#FFC600", finish: "silk" },

  // --- Bambu PLA Silk Dual Colour ---
  "gilded rose": { hex: "#E39BB4", hex2: "#D4A017", finish: "dual" },
  "neon city": { hex: "#2E7BD6", hex2: "#D42E9E", finish: "dual" },

  // --- Bambu PLA Sparkle and Galaxy ---
  "13101": { hex: "#101010", finish: "sparkle" },
  "13602": { hex: "#7B4E9E", finish: "sparkle" },
  "crimson red sparkle": { hex: "#792B36", finish: "sparkle" },
  "royal purple sparkle": { hex: "#483D8B", finish: "sparkle" },

  // --- Bambu PLA Tough ---
  "tough black": { hex: "#25282A", finish: "basic" },
  "pine green": { hex: "#00482B", finish: "basic" },
  "black": { hex: "#25282A", finish: "basic" },

  // --- Bambu CMYK lithophane bundle ---
  "litho cyan": { hex: "#00A5DF", finish: "basic" },
  "litho magenta": { hex: "#EC008C", finish: "basic" },
  "litho yellow": { hex: "#F4EE2A", finish: "basic" },
  "litho black": { hex: "#0D0D0D", finish: "basic" },

  // --- Bambu PETG ---
  "30100": { hex: "#FFFFFF", finish: "basic" },
  "30101": { hex: "#0D0D0D", finish: "basic" },
  "30104": { hex: "#E8E3D9", finish: "basic" },
  "30401": { hex: "#D4A017", finish: "basic" },
  "30602": { hex: "#0086D6", finish: "basic" },
  "30700": { hex: "#6B3FA0", finish: "basic" },
  "32101": { hex: "#EBF0EE", finish: "translucent" },
  "32500": { hex: "#7A8B3F", finish: "translucent" },
  "white": { hex: "#FFFFFF", finish: "basic" },

  // --- Bambu support and soluble ---
  "65102": { hex: "#EDE7DC", finish: "basic" },
  "66400": { hex: "#F0F4F2", finish: "translucent" },
  "support for pla": { hex: "#1A1A1A", finish: "basic" },
  "support for pa/pet": { hex: "#EDE7DC", finish: "basic" },

  // --- Amazon, third party ---
  "overture:pla plus (pla+):digital blue": { hex: "#0A84D6", finish: "basic" },
  "duramic 3d:petg:purple": { hex: "#7A3FB5", finish: "basic" },
  "duramic 3d:petg:yellow": { hex: "#F2C60E", finish: "basic" },
  "duramic 3d:petg:pink": { hex: "#F06FA8", finish: "basic" },
  "duramic 3d:petg:translucent green": { hex: "#2E965A", finish: "translucent" },
  "duramic 3d:pla plus (pla+):purple": { hex: "#6B3FA0", finish: "basic" },
  "duramic 3d:pla plus (pla+):white": { hex: "#FFFFFF", finish: "basic" },
  "creality:hyper pla:black": { hex: "#111111", finish: "basic" },
  "creality:hyper pla:grey": { hex: "#8A8F92", finish: "basic" },
  "giantarm:pla glow in the dark:rainbow": { hex: "#8FD0F0", finish: "glow" },
  "tronxy:pla glow in the dark bundle:green / purple / orange-red": {
    hex: "#5FBF7A", finish: "glow",
  },
  "anycubic:silk pla:silk light gold": { hex: "#E8C87A", finish: "silk" },
  "giantarm:petg:clear / transparent": { hex: "#EBF0EE", finish: "translucent" },
  "cc3d:temp colour change pla:green to yellow": {
    hex: "#3F9E5B", hex2: "#EDE04A", finish: "dual",
  },
  "unbranded:pla+ colour change:rainbow": { hex: "#E24B4B", finish: "rainbow" },
  "cc3d:silk pla:purple": { hex: "#7C3FBF", finish: "silk" },
  "giantarm:petg:metal green": { hex: "#1E7A4A", finish: "silk" },
  "cc3d:marble petg:stone rock": { hex: "#D8D5CE", finish: "marble" },
};

/**
 * @param {string} key
 * @returns {Swatch | undefined}
 */
export function lookupColour(key) {
  return COLOURS[key.trim().toLowerCase()];
}
