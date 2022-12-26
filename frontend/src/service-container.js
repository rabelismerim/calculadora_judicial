import amostrasRepository from "./repositories/amostras";

//add repositories here

export default {
    amostrasRepository,
  };


// Example dynamic injection of dependancies 
// Referance: https://markus.oberlehner.net/blog/the-ioc-container-pattern-with-vue/

// const RepositoryInterface = {
//     find() {},
//     list() {}
//   };

//   function bind(repositoryFactory, Interface) {
//     return {
//       ...Object.keys(Interface).reduce((prev, method) => {
//         const resolveableMethod = async (...args) => {
//         const repository = await repositoryFactory();
//         return repository.default[method](...args);
//         };
//         return { ...prev, [method]: resolveableMethod };
//       }, {}),
//     };
//   }
 
//   export default {
//     get projectRepository() {
//       // Delay loading  until a method of the repository is called.
//       return bind(() => import('./repositories/projetos'), RepositoryInterface);
//     },
//     get userRepository() {
//     // Load the repository immediately when it's injected.
//         const userRepositoryPromise = import('./repositories/user');
//         return bind(() => userRepositoryPromise, RepositoryInterface);
//  },
//  get unidadeRepository() {
//     // Load the repository immediately when it's injected.
//         const unidadeRepositoryPromise = import('./repositories/unidade');
//         return bind(() => unidadeRepositoryPromise, RepositoryInterface);
//  },
//  get requestRepository() {
//     // Load the repository immediately when it's injected.
//         const requestRepositoryPromise = import('./repositories/request');
//         return bind(() => requestRepositoryPromise, RepositoryInterface);
//  },

//   };

