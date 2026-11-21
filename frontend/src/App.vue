<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <nav class="navbar bg-base-100 shadow-sm">
      <div class="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-2 px-2">
        <RouterLink class="btn btn-ghost text-lg" to="/">Deep Dive Interview</RouterLink>
        <ul class="menu menu-horizontal ml-auto gap-1 px-0">
          <li><RouterLink to="/" exact-active-class="menu-active">Interviews</RouterLink></li>
          <li><RouterLink to="/history" active-class="menu-active">History</RouterLink></li>
          <li><RouterLink to="/resume" active-class="menu-active">Résumé</RouterLink></li>
        </ul>
      </div>
    </nav>
    <RouterView />
  </div>
</template>
