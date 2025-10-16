import type { ReactNode } from 'react'

export default function AppLayout({ children }: { children: ReactNode }): JSX.Element {
  return <div className="min-h-[100vh]">{children}</div>
}


