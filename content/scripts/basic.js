/*
console.log("basic.js 已成功載入！")

// -------------------------
// 測試 1：改變文字
// -------------------------

const helloButton = document.getElementById("hello-btn")
const helloText = document.getElementById("hello-text")

if (helloButton && helloText) {
  helloButton.addEventListener("click", function () {
    helloText.textContent = "JavaScript 執行成功！"
  })
}


// -------------------------
// 測試 2：簡單計數器
// -------------------------

const countButton = document.getElementById("count-btn")
const countNumber = document.getElementById("count-number")

let count = 0

if (countButton && countNumber) {
  countButton.addEventListener("click", function () {
    count = count + 1
    countNumber.textContent = count
  })
}
*/

console.log("basic.js 已載入")

function setupBasicJS() {
  // =========================
  // 1. 文字按鈕
  // =========================

  const helloButton = document.getElementById("hello-btn")
  const helloText = document.getElementById("hello-text")

  if (helloButton && helloText && !helloButton.dataset.jsReady) {

    helloButton.dataset.jsReady = "true"

    helloButton.addEventListener("click", function () {
      helloText.textContent = "JavaScript 執行成功！"
    })
  }


  // =========================
  // 2. 計數器
  // =========================

  const countButton = document.getElementById("count-btn")
  const countNumber = document.getElementById("count-number")

  if (countButton && countNumber && !countButton.dataset.jsReady) {

    countButton.dataset.jsReady = "true"

    let count = 0

    countButton.addEventListener("click", function () {
      count++
      countNumber.textContent = count
    })
  }
}


// 第一次正常開啟頁面
setupBasicJS()


// Quartz SPA 換頁之後重新初始化
document.addEventListener("nav", setupBasicJS)