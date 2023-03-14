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
