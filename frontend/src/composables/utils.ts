export const toUpperCase = (text: string) => text.toUpperCase()

export const formatDate = (date: string) => new Date(date)
  .toLocaleDateString()
  .padStart(10, '0')

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
