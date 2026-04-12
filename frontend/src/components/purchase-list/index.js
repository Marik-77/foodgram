import styles from './styles.module.css'
import cn from 'classnames'
import { Purchase } from '../index'

const PurchaseList = ({ orders = [], handleRemoveFromCart }) => {
  return <ul className={styles.purchaseList}>
    {orders.map(order => <Purchase
      handleRemoveFromCart={handleRemoveFromCart}
      key={order.id}
      {...order}
    />)}
  </ul>
}

export default PurchaseList
