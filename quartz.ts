/*
import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
*/

import {
  loadQuartzConfig,
  loadQuartzLayout,
} from "./quartz/plugins/loader/config-loader"

import { CustomScripts } from "./quartz/custom/CustomScripts"


const config = await loadQuartzConfig()


// =========================
// 自訂網站 JavaScript
// =========================

config.plugins.transformers.push(
  CustomScripts(),
)


export default config

export const layout = await loadQuartzLayout()