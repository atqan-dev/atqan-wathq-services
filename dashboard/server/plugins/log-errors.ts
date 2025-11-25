import logger from '../utils/logger'

export default defineNitroPlugin((nitroApp) => {
  nitroApp.hooks.hook('error', (error, event) => {
    const req = event?.node?.req
    logger.error('Server error', {
      error,
      url: req?.url,
      method: req?.method,
      ip: req?.socket?.remoteAddress
    })
  })
}) 