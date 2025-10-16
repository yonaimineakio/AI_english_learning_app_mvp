import { clsx, ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatMinutes = (minutes: number) => `${minutes}分`

export const calculateEstimatedMinutes = (rounds: number) => rounds * 3

