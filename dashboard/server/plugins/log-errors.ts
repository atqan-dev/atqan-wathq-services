import logger from '../utils/logger'

export default defineNitroPlugin((nitroApp) => {
  nitroApp.hooks.hook('error', (error, event) => {
    logger.error('Server error', {
      error,
      url: (event.node as any).req.url,
      method: (event.node as any).req.method,
      ip: (event.node as any).req.socket.remoteAddress
    })
  })
}) 