import React, { useState, useRef, useEffect } from "react";
import api, { formatApiError } from '../api'

export default function useSubscriptions () {
  const [ subscriptions, setSubscriptions ] = useState([])
  const [ subscriptionsPage, setSubscriptionsPage ] = useState(1)
  const [ subscriptionsCount, setSubscriptionsCount ] = useState(0)
  const subscriptionsPageRef = useRef(subscriptionsPage)

  useEffect(() => {
    subscriptionsPageRef.current = subscriptionsPage
  }, [subscriptionsPage])

  const removeSubscription = ({ id, callback }) => {
    api
      .deleteSubscriptions({ author_id: id })
      .then(() =>
        api.getSubscriptions({
          page: subscriptionsPageRef.current,
          limit: 6,
          recipes_limit: 3,
        })
      )
      .then((res) => {
        setSubscriptions(res.results)
        setSubscriptionsCount(res.count)
        callback && callback()
      })
      .catch((err) => {
        alert(formatApiError(err))
      })
  }
  
  return {
    subscriptions,
    setSubscriptions,
    subscriptionsPage,
    setSubscriptionsPage,
    removeSubscription,
    subscriptionsCount,
    setSubscriptionsCount
  }
}
