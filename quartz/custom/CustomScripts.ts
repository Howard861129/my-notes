import type { QuartzTransformerPlugin } from "../plugins/types"

// @ts-expect-error Quartz 會將 .inline.ts 打包成瀏覽器 JavaScript
import basicScript from "./scripts/basic.inline"

export const CustomScripts: QuartzTransformerPlugin = () => {
  return {
    name: "CustomScripts",

    externalResources() {
      return {
        js: [
          {
            script: basicScript,
            loadTime: "afterDOMReady",
            contentType: "inline",
          },
        ],
      }
    },
  }
}