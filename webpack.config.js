const path = require('path');
const webpack = require('webpack');
const { styles } = require('@ckeditor/ckeditor5-dev-utils');
const CKEditorWebpackPlugin = require('@ckeditor/ckeditor5-dev-webpack-plugin');
const TerserWebpackPlugin = require('terser-webpack-plugin');

module.exports = {
    devtool: 'source-map',
    performance: { hints: false },
    entry: path.resolve(__dirname, 'src/ckeditor.js'),
    output: {
        path: path.resolve(__dirname, 'static/js/ckeditor'),
        filename: 'ckeditor.js',
        library: 'DecoupledEditor',
        libraryTarget: 'umd',
        libraryExport: 'default'
    },
    optimization: {
        minimizer: [
            new TerserWebpackPlugin({
                terserOptions: {
                    output: {
                        comments: /^!/
                    }
                },
                extractComments: false
            })
        ]
    },
    plugins: [
        new CKEditorWebpackPlugin({
            language: 'tr',
            additionalLanguages: ['en']
        }),
        new webpack.BannerPlugin({
            banner: 'KolayCMS CKEditor build',
            raw: true
        })
    ],
    module: {
        rules: [
            {
                test: /ckeditor5-[^/\\]+[/\\]theme[/\\]icons[/\\][^/\\]+\.svg$/,
                use: ['raw-loader']
            },
            {
                test: /ckeditor5-[^/\\]+[/\\]theme[/\\].+\.css$/,
                use: [
                    {
                        loader: 'style-loader',
                        options: {
                            injectType: 'singletonStyleTag',
                            attributes: {
                                'data-cke': true
                            }
                        }
                    },
                    'css-loader',
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: styles.getPostCssConfig({
                                themeImporter: {
                                    themePath: require.resolve('@ckeditor/ckeditor5-theme-lark')
                                },
                                minify: true
                            })
                        }
                    }
                ]
            }
        ]
    }
}; 