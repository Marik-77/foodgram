import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>Технологии</title>
      <meta name="description" content="Фудграм — технологии проекта" />
      <meta property="og:title" content="Технологии" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <p className={styles.textItem}>
            Ниже перечислены основные технологии, на которых построен сервис Foodgram: бэкенд на Django,
            фронтенд на React и развёртывание через Docker и Nginx.
          </p>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>Python</li>
              <li className={styles.textItem}>Django</li>
              <li className={styles.textItem}>Django REST Framework</li>
              <li className={styles.textItem}>Djoser</li>
              <li className={styles.textItem}>PostgreSQL</li>
              <li className={styles.textItem}>React, React Router</li>
              <li className={styles.textItem}>Docker, Docker Compose</li>
              <li className={styles.textItem}>Nginx</li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

