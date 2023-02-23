export const toUpperCase = (text: string) => text.toUpperCase()

export const formatDate = (date: string) => new Date(date)
  .toLocaleDateString()
  .padStart(10, '0')
