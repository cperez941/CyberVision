%% Author : PJ DeFatta
%% Date : 24 Feb 2018
%% Description : Image blending across three pi cameras derived from
%% and using the MatLab online tutorial, blends images and plots points
%% on features

%% DEBUG MODE
Debug = 1;

%% Connect to the Raspberry Pis
myPi1 = raspi('192.168.2.8', 'pi','PasswordHere');
myPi2 = raspi('192.168.2.14', 'pi','PasswordHere');
myPi3 = raspi('192.168.2.4', 'pi','PasswordHere');

%% Initialize the Raspberry Pi Boards
myCam1 = cameraboard(myPi1, 'Resolution', '1280x720');
myCam2 = cameraboard(myPi2, 'Resolution', '1280x720');
myCam3 = cameraboard(myPi3, 'Resolution', '1280x720');

%% Take a Snapshot and save the images
snap1 = snapshot(myCam1);
snap2 = snapshot(myCam2);
snap3 = snapshot(myCam3);

%Flip the middle camera's image
imgMirror = flipdim(snap3,1);

%Save the images
imwrite(snap1, 'snap1.png');
imwrite(snap2, 'snap3.png');
imwrite(imgMirror, 'snap2.png');

% Load images into a imageDataStore
snapshotgDir = fullfile({'snap1.png', 'snap2.png', 'snap3.png'});
snapshotScene = imageDatastore(snapshotgDir);

% Display images to be stitched
%montage(snapshotScene.Files)

%% Register Image Pairs
% To create the panorama, start by registering successive image pairs using
% the following procedure:
%
% # Detect and match features between $I(n)$ and $I(n-1)$.
% # Estimate the geometric transformation, $T(n)$, that maps $I(n)$ to $I(n-1)$.
% # Compute the transformation that maps $I(n)$ into the panorama image as $T(n) * T(n-1) * ... * T(1)$.

% Read the first image from the image set.
Image = readimage(snapshotScene, 1);

% Initialize features for Image[1]
grayImage = rgb2gray(Image);
points = detectSURFFeatures(grayImage,'MetricThreshold', 998.0);
points100 = selectStrongest(points, 100);

if(Debug ==1)
    %Create a figure with the strongest 100 points
    figure;
    imshow(Image);
    title('Top 100 Feature Points on Image');
    hold on;
    plot(points100);
    [features100, points100] = extractFeatures(grayImage, points100);
end

[features, points] = extractFeatures(grayImage, points);

% Initialize all the transforms to the identity matrix --> eye(n) = identity matrix with dim nxn.
numOfImages = numel(snapshotScene.Files);
%Use this transform if objects are failry close
tforms(numOfImages) = projective2d(eye(3));
%Use this transfrom if objects are farther away
%tforms(numOfImages) = affine2d(eye(3));

% Iterate over remaining image pairs
for n = 2:numOfImages

    % Store points and features for Image(n-1).
    pointsPrevious = points;
    featuresPrevious = features;

    if(Debug == 1)
        featuresPrevious100 = features100;
        points100Prev = points100;
    end

    % Read the current image.
    Image = readimage(snapshotScene, n);

    % Detect and extract SURF features for Image[n].
    grayImage = rgb2gray(Image);
    points = detectSURFFeatures(grayImage, 'MetricThreshold', 998.0);
    points100 = selectStrongest(points, 100);

    if(Debug == 1)
        %Create a figure with the strongest 100 points
        figure;
        imshow(Image);
        title('Top 100 Feature Points on Image');
        hold on;
        plot(points100);
        [features100, points100] = extractFeatures(grayImage, points100);
    end

    [features, points] = extractFeatures(grayImage, points);

    if(Debug == 1)
        %Create a figure that shows the maching points from the strongest 100 points
        imagePrevious = readimage(snapshotScene, n-1);
        imagePairs = matchFeatures(featuresPrevious100, features100);
        matchedImage1Points = points100Prev(imagePairs(:, 1), :);
        matchedImage2Points = points100(imagePairs(:, 2), :);
        figure;
        showMatchedFeatures(imagePrevious, Image, matchedImage1Points, ...
        matchedImage2Points, 'montage');
        title('Matched Points From 100 Strongest Points');
    end

    % Find correspondences between Image[n] and Image[n-1].
    indexPairs = matchFeatures(features, featuresPrevious, 'Unique', true);

    matchedPoints = points(indexPairs(:,1), :);
    matchedPointsPrev = pointsPrevious(indexPairs(:,2), :);

    % Estimate the transformation between I(n) and I(n-1).
    tforms(n) = estimateGeometricTransform(matchedPoints, matchedPointsPrev,...
        'projective', 'Confidence', 99.9999, 'MaxNumTrials', 80000);

    % Compute T(n) * T(n-1) * ... * T(1)
    %__.T => Transpose of a matrix
    tforms(n).T = tforms(n).T * tforms(n-1).T;
end

%% Find the Center Image
% Start by using the |projective2d| |outputLimits| method to find the
% output limits for each transform. The output limits are then used to
% automatically find the image that is roughly in the center of the scene.

imageSize = size(Image);  % all the images are the same size

% Compute the output limits  for each transform
for i = 1:numel(tforms)
    [xlim(i,:), ylim(i,:)] = outputLimits(tforms(i), [1 imageSize(2)], [1 imageSize(1)]);
end

%%
% Next, compute the average X limits for each transforms and find the image
% that is in the center. Only the X limits are used here because the scene
% is known to be horizontal. If another set of images are used, both the X
% and Y limits may need to be used to find the center image.

avgXLim = mean(xlim, 2);

[~, idx] = sort(avgXLim);

centerIdx = floor((numel(tforms)+1)/2);

centerImageIdx = idx(centerIdx);

%%
% Finally, apply the center image's inverse transform to all the others.

Tinv = invert(tforms(centerImageIdx));

for i = 1:numel(tforms)
    tforms(i).T = tforms(i).T * Tinv.T;
end

%% Initialize the Panorama
% Now, create an initial, empty, panorama into which all the images are
% mapped.
%
% Use the |outputLimits| method to compute the minimum and maximum output
% limits over all transformations. These values are used to automatically
% compute the size of the panorama.

for i = 1:numel(tforms)
    [xlim(i,:), ylim(i,:)] = outputLimits(tforms(i), [1 imageSize(2)], [1 imageSize(1)]);
end

% Find the minimum and maximum output limits
xMin = min([1; xlim(:)]);
xMax = max([imageSize(2); xlim(:)]);

yMin = min([1; ylim(:)]);
yMax = max([imageSize(1); ylim(:)]);

% Width and height of panorama.
width  = round(xMax - xMin);
height = round(yMax - yMin);

% Initialize the "empty" panorama.
panorama = zeros([height width 3], 'like', Image);

%% Create the Panorama
% Use |imwarp| to map images into the panorama and use
% |vision.AlphaBlender| to overlay the images together.

blender = vision.AlphaBlender('Operation', 'Binary mask', ...
    'MaskSource', 'Input port');

% Create a 2-D spatial reference object defining the size of the panorama.
xLimits = [xMin xMax];
yLimits = [yMin yMax];
panoramaView = imref2d([height width], xLimits, yLimits);

% Create the panorama.
for i = 1:numOfImages

    Image = readimage(snapshotScene, i);

    % Transform Image into the panorama.
    warpedImage = imwarp(Image, tforms(i), 'OutputView', panoramaView);

    % Generate a binary mask.
    mask = imwarp(true(size(Image,1),size(Image,2)), tforms(i), 'OutputView', panoramaView);

    % Overlay the warpedImage onto the panorama.
    panorama = step(blender, panorama, warpedImage, mask);
end

figure
imshow(panorama)

%% References
% [1] Matthew Brown and David G. Lowe. 2007. Automatic Panoramic Image
%     Stitching using Invariant Features. Int. J. Comput. Vision 74, 1
%     (August 2007), 59-73.
