export const printError = (message: string, error: any) => {
  if (import.meta.env.VITE_LOG)
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

export const formatLegalNumber = (value: string) => {
  value = value.replace(/[./-]/gi, '')
  if (value.length < 14) {
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

export const redirectTo = (url: string) => window.location.replace(url)

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
