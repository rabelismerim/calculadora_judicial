export const printError = (message: string, error: any) => {
  if (import.meta.env.VITE_LOG === 'true')
    console.warn(message, error)
}

export const toUpperCase = (text = '') => text.toUpperCase()

export const formatDate = (date: string) => new Date(date)
  .toLocaleDateString()
  .padStart(10, '0')

export const formatDateToBackend = (value: string) => {
  if (!value)
    return
  const [day, month, year] = value.split('/')
  return `${year}-${month}-${day}`
}
export const formatDateFromBackend = (value: string) => {
  if (!value)
    return
  const [year, month, day] = value.slice(0, 10).split('-')
  return `${day}/${month}/${year}`
}
export const formatDateHour = (value: string) => {
  if (!value)
    return
  const [year, month, day] = value.slice(0, 10).split('-')
  return `${day}/${month}/${year} às ${value.slice(11, 19)}`
}
export const formatDay = (value: string) => {
  if (!value)
    return
  const [, month, day] = value.slice(0, 10).split('-')
  return `${day}/${month}`
}
export const formatMonth = (value: string) => {
  if (!value)
    return
  const months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
  const [, month] = value.slice(0, 10).split('-')
  return months[+month - 1] || ''
}

export const formatNumber = (value: number | undefined, digits = 6) => value
  ?.toLocaleString('pt-BR', { maximumFractionDigits: digits, minimumFractionDigits: digits })

export const getValidNumber = (value: string) => {
  const num = value
    .replace(/((?![0-9.,]).)*/g, '')
  const getCharCount = (char: string, value: string) => value
    .split(char).length - 1
  const dotsCount = getCharCount('.', num)
  const commaCount = getCharCount(',', num)
  if (!num)
    return 0
  if (commaCount === 1 && dotsCount === 1) {
    const values = value.split(/[.,]/)
    const last = values.at(-1)
    const start = values.slice(0, values.length - 1).join('')
    return Number(`${start}.${last}`)
  }
  if (commaCount === 1) {
    return Number(num
      .replaceAll('.', '')
      .replace(',', '.'))
  }
  if (dotsCount === 1) {
    return Number(num
      .replaceAll(',', ''))
  }
  return Number(num.replaceAll('.', '').replaceAll(',', ''))
}

export const formatLegalNumber = (value: string) => {
  if (!value)
    return
  value = value?.replace(/[./-]/gi, '')
  if (value?.length < 14) {
    const [,first, second, third, digit] = value
      .padEnd(11, '0')
      .split(/^(\d{3})(\d{3})(\d{3})(\d{2})/)
    return `${first}.${second}.${third}-${digit}`
  }

  const [,first, second, third, fourth, digit] = value
    .padEnd(14, '0')
    .split(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/)
  return `${first}.${second}.${third}/${fourth}-${digit}`
}

export const getInitials = (text = '') => {
  const initials = text
    .toUpperCase()
    .split(' ')
    .map((word: string) => word[0])
    .join('')
  if (initials.length < 2)
    return text.toUpperCase().slice(0, 2)
  if (initials.length > 2)
    return initials.slice(0, 2)
  return initials
}

export const getValidDate = (value: string) => {
  const months: any = {
    jan: 1,
    janeiro: 1,
    fev: 2,
    fevereiro: 2,
    mar: 3,
    março: 3,
    abr: 4,
    abril: 4,
    mai: 5,
    maio: 5,
    jun: 6,
    junho: 6,
    jul: 7,
    julho: 7,
    ago: 8,
    agosto: 8,
    set: 9,
    setembro: 9,
    out: 10,
    outubro: 10,
    nov: 11,
    novembro: 11,
    dez: 12,
    dezembro: 12,
  }
  if (value.match(/\w{3,}[-/]\d{2,4}/)) {
    const [month, year] = value.split(/[-/]/)
    const useMonth = months[month]
    const formatedMonth = (`${useMonth}`).padStart(2, '0')
    const useYear = year.length === 2 ? `20${year}` : year
    if (!useMonth)
      return ''
    return `${useYear}-${formatedMonth}-01`
  }
  if (value.match(/^\d{1,2}[-/]\d{2,4}$/)) {
    const [month, year] = value.split(/[-/]/)
    return `${year}-${month}-01`
  }
  if (value.match(/^\d{1,2}[-/]\d{1,2}[-/]\d{1,4}$/)) {
    const [day, month, year] = value.split(/[-/]/)
    return `${year}-${month}-${day}`
  }
  const date = new Date(value)
  const day = date.getDate()
  const month = date.getMonth() + 1
  const year = date.getFullYear()
  const values = [year, month, day]
  if (values.some(item => isNaN(item)))
    return ''
  return `${year}-${(`${month}`).padStart(2, '0')}-${(`${day}`).padStart(2, '0')}`
}

export const redirectTo = async (url: string) => {
  window.location.href = url
}

export const clone = (object: any) => JSON.parse(JSON.stringify(object))

export const delay = (seconds: number) => new Promise(resolve =>
  setTimeout(() => resolve(true), seconds * 1000))

const sum = (array: number[], start: number) =>
  array.reduce((total, el, i) => total + el * (start - i), 0)
const rest = (value: number) => value % 11
const format = (value: string) => value.replace(/[^\d]+/g, '')
const isValidNumber = (value: string, count: number) =>
  format(value).length === count && !format(value).match(/(\d)\1{10}/)
const validator = (value: string) => format(value)
  .split('')
  .splice(format(value).length - 2)
  .map(el => +el)
const validate = (firstDigit: number, lastDigit: number, validator: number[]) =>
  firstDigit === validator[0] && lastDigit === validator[1]
const toValidate = (value: string, end: number, start = 0) => format(value)
  .split('')
  .filter((digit, index) => index >= start && index <= end && digit)
  .map(el => +el)

export const isValidCPF = (cpf: string) => {
  if (!isValidNumber(cpf, 11))
    return false
  const digit = (end: number, factor: number) =>
    rest(sum(toValidate(cpf, end), factor) * 10) % 10
  const firstDigit = digit(8, 10)
  const lastDigit = digit(9, 11)
  return validate(firstDigit, lastDigit, validator(cpf))
}

export const isValidCNPJ = (cnpj: string) => {
  if (!isValidNumber(cnpj, 14))
    return false
  const digit = (sum: number) => rest(sum) < 2 ? 0 : 11 - rest(sum)
  const firstDigit = digit(sum(toValidate(cnpj, 3), 5) + sum(toValidate(cnpj, 11, 4), 9))
  const lastDigit = digit(sum(toValidate(cnpj, 4), 6) + sum(toValidate(cnpj, 12, 5), 9))
  return validate(firstDigit, lastDigit, validator(cnpj))
}

export const rangeBetween = (start = 0, end = 0, count = 1) => Array(count < 0 ? 0 : count).fill(0)
  .map((_, i) => start + ((end - start) / (count <= 1 ? 1 : count - 1) * i))

export const flatten = (data: any) => {
  const result: any = {}
  function recurse(cur: any, prop: any) {
    if (Object(cur) !== cur) {
      result[prop] = cur
    }
    else if (Array.isArray(cur)) {
      const l = cur.length
      for (let i = 0; i < l; i++)
        recurse(cur[i], `${prop}[${i}]`)
      if (l === 0)
        result[prop] = []
    }
    else {
      let isEmpty = true
      for (const p in cur) {
        isEmpty = false
        recurse(cur[p], prop ? `${prop}.${p}` : p)
      }
      if (isEmpty && prop)
        result[prop] = {}
    }
  }
  recurse(data, '')
  return result
}

export const unflatten = (data: any) => {
  if (Object(data) !== data || Array.isArray(data))
    return data
  const regex = /\.?([^.\[\]]+)|\[(\d+)\]/g
  const resultholder: any = {}
  for (const p in data) {
    let cur = resultholder
    let prop = ''
    let m = regex.exec(p)
    while (m) {
      cur = cur[prop] || (cur[prop] = (m[2] ? [] : {}))
      prop = m[2] || m[1]
      m = regex.exec(p)
    }
    cur[prop] = data[p]
  }
  return resultholder[''] || resultholder
}

export const parseToCamel = (data: any) => unflatten(Object
  .fromEntries(Object.entries(flatten(data))
    .map(([key, value]) => {
      const regex = /(\[\d+\]|\.)/
      return [
        key.split(regex)
          .map(item => item.match(regex) ? item : toCamel(item))
          .join(''),
        value,
      ]
    }),
  ))

export const parseToSnake = (data: any) => unflatten(Object
  .fromEntries(Object.entries(flatten(data))
    .map(([key, value]) => {
      const regex = /(\[\d+\]|\.)/
      return [
        key.split(regex)
          .map(item => item.match(regex) ? item : toSnake(item))
          .join(''),
        value,
      ]
    }),
  ))

export const saveFile = (data: any, fileName = 'download', fileExtension = 'txt') => {
  const getType = () => {
    if (['jpg', 'jpeg'].includes(fileExtension))
      return 'image/jpeg'
    if (['png', 'apng'].includes(fileExtension))
      return 'image/png'
    if (['gif'].includes(fileExtension))
      return 'image/gif'
    if (['pdf'].includes(fileExtension))
      return 'application/pdf'
    if (['xlsx'].includes(fileExtension))
      return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    if (['html'].includes(fileExtension))
      return 'text/html'
    return 'text/plain'
  }

  const blob = (() => {
    if (data instanceof Blob)
      return data
    if (fileExtension === 'csv')
      return new Blob([new Uint8Array([239, 187, 191]), 'Text', data], { type: 'text/plain;charset=utf-8' })
    return new Blob([data], { type: getType() })
  })()

  const link = document.createElement('a')
  const url = window.webkitURL != null
    ? window.webkitURL.createObjectURL(blob)
    : window.URL.createObjectURL(blob)

  document.body.appendChild(link)
  link.style.display = 'none'
  link.href = url
  link.download = `${fileName}.${fileExtension}`
  link.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(link)
}

export const downloadFile = (textToWrite: string, fileNameToSaveAs: string, contentType = 'application/xlsx') => {
  const byteCharacters = atob(textToWrite)
  const byteNumbers = byteCharacters
    .split('')
    .map((_, index) => byteCharacters.charCodeAt(index))
  const byteArray = new Uint8Array(byteNumbers)
  const blob = new Blob([byteArray], { type: contentType })
  const downloadLink = document.createElement('a')
  downloadLink.download = fileNameToSaveAs
  downloadLink.innerHTML = 'Download File'
  if (window.webkitURL != null) {
    downloadLink.href = window.webkitURL.createObjectURL(blob)
  }
  else {
    downloadLink.href = window.URL.createObjectURL(blob)
    downloadLink.onclick = () => {
      document.body.removeChild(downloadLink)
    }
    downloadLink.style.display = 'none'
    document.body.appendChild(downloadLink)
  }
  downloadLink.click()
}

export const deleteAllCookies = () => {
  document.cookie
    .split(';')
    .forEach((cookie) => {
      const eqPos = cookie.indexOf('=')
      const name = eqPos > -1 ? cookie.slice(0, eqPos) : cookie
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT`
    })
}
