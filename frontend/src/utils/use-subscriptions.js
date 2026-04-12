import React, { useState } from "react";
import { useTags } from './index.js'
import api from '../api'

export default function useRecipes () {
  const [ subscriptions, setSubscriptions ] = useState([])
  const [ subscriptionsPage, setSubscriptionsPage ] = useState(1)
  const [ subscriptionsCount, setSubscriptionsCount ] = useState(0)

  const removeSubscription = ({ id, callback }) => {
    const idNum = Number(id)
    api
      .deleteSubscriptions({ author_id: id })
      .then(res => {
        setSubscriptions((prev) =>
          prev.filter((item) => Number(item.id) !== idNum)
        )
        setSubscriptionsCount((c) => c - 1)
        callback && callback()
      })
      .catch(err => {
        const { errors } = err
        if (errors) {
          alert(errors)
        }
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
