import { useRouter, useRoute } from 'vue-router'

export function useAppRouter() {
  const router = useRouter()
  const route = useRoute()

  const navigate = (path: string) => router.push(path)

  return { router, route, navigate }
}
