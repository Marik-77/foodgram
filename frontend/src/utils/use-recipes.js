import React, { useState } from "react";
import { useTags } from './index.js'
import api, { formatApiError } from '../api'

export default function useRecipes () {
  const [ recipes, setRecipes ] = useState([])
  const [ recipesCount, setRecipesCount ] = useState(0)
  const [ recipesPage, setRecipesPage ] = useState(1)
  const { value: tagsValue, handleChange: handleTagsChange, setValue: setTagsValue } = useTags()

  const handleLike = ({ id, toLike = true }) => {
    const method = toLike ? api.addToFavorites.bind(api) : api.removeFromFavorites.bind(api)
    method({ id }).then(res => {
      const recipesUpdated = recipes.map(recipe => {
        if (recipe.id === id) {
          recipe.is_favorited = toLike
        }
        return recipe
      })
      setRecipes(recipesUpdated)
    })
    .catch((err) => {
      alert(formatApiError(err))
    })
  }

  const handleAddToCart = ({ id, toAdd = true, callback }) => {
    const method = toAdd ? api.addToOrders.bind(api) : api.removeFromOrders.bind(api)
    const idNum = Number(id)
    method({ id }).then(res => {
      setRecipes((prev) =>
        prev.map((recipe) =>
          Number(recipe.id) === idNum
            ? { ...recipe, is_in_shopping_cart: toAdd }
            : recipe
        )
      )
      callback && callback(toAdd)
    })
    .catch((err) => {
      alert(formatApiError(err))
    })
  }

  return {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    handleLike,
    handleAddToCart,
    handleTagsChange,
    setTagsValue
  }
}
