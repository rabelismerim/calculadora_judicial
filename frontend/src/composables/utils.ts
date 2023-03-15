export const toUpperCase = (text: string) => text.toUpperCase()

export const formatDate = (date: string) => new Date(date)
  .toLocaleDateString()
  .padStart(10, '0')

export const formatDateBackend = (value: string) => {
  const [day, month, year] = value.split('/')
  return `${year}-${month}-${day}`
}

export const getInitials = (text: string) => {
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
