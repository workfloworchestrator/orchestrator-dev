module.exports = {

    // This is the original configuration content from next.config.js in example-orchestrator-ui:

    reactStrictMode: false,
    output: 'standalone',
    i18n: {
        // These are all the locales you want to support in
        // your application
        locales: ['en-GB', 'nl-NL'],
        defaultLocale: 'en-GB',
    },
    transpilePackages: [
        '@copilotkit/react-core',
        '@orchestrator-ui/orchestrator-ui-components',
    ],
    webpack: (config, { dev, isServer }) => {
        if (dev) {
            // This effectively excludes orchestrator-ui-components from being managed by Next.js's default snapshot mechanism.
            // When deciding whether to rebuild, Next.js will no longer go by just the package version
            // (the default for anything in node_modules), but by individual file differences.
            config.snapshot = {
                ...(config.snapshot || {}),
                managedPaths: [
                    /^(.+?[\\/]node_modules[\\/](?!(@orchestrator-ui[\\/]orchestrator-ui-components))(@.+?[\\/])?.+?)[\\/]/,
                ],
            };
            // We also need to explicitly exclude the module from being ignored by the watch mechanism,
            // since by default everything in node_modules is ignored.
            config.watchOptions = {
                ...(config.watchOptions || {}),
                ignored: [
                    'node_modules/!(@orchestrator-ui/orchestrator-ui-components)/dist/**',
                ]
            };
        }
        return config;
    },
    // Turbopack is now the default, need an empty turbopack config to disable for webpack.
    turbopack: {},
};
